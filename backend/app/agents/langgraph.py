import os
import json
import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from app.models.schemas import TripRequest, TripPlan
from langgraph.graph import END, StateGraph
from langchain_core.messages import AnyMessage, AIMessage
from typing import Annotated, Optional, TypedDict
import operator
from .prompt import ATTRACTION_AGENT_PROMPT, WEATHER_AGENT_PROMPT, HOTEL_AGENT_PROMPT, PLANNER_AGENT_PROMPT

AMAP_API_KEY="223f5fc1a756b4cae5d93bd91295a3ab"
llm = ChatOpenAI(
    model="MiniMax-M2.1",
    api_key="sk-api-E3VIM6GG9h7tk4gZ7sTBmt9HzyNaNeqXesHElewlPEvYcGGbUt898u9mfaK5p5GXF0xYAllVT1iI-srH4Cc5YLoEBxyHmSUAT-uwxmHjXeoYuD8srti4nOw",
    base_url="https://api.minimaxi.com/v1",
    temperature=0.0
)

async def get_mcp_tools():
    # Stdio Mode
    client = MultiServerMCPClient({
        "amap-mcp-server":{
            "command": "uvx",
            "args": ["amap-mcp-server"],
            "env": {"AMAP_MAPS_API_KEY": AMAP_API_KEY}, 
            "transport": "stdio"
        }
    })

    # SSE Mode
    # client = MultiServerMCPClient({
    #     "amap-amap-sse": {
    #         "url": f"https://mcp.amap.com/sse?key={AMAP_API_KEY}",
    #         "transport": "sse"
    #     }
    # })
    # 异步获取 MCP 工具
    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tools from Amap MCP server.")
    return tools

async def init_agent(name: str, system_prompt: str, tools: list = None):
    agent = create_agent(
        name=name,
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    return agent

def _make_query_handler(agent, prompt_builder, state_field) -> callable:
    async def call_agent(state: AgentState) -> AgentState:
        request = state.get("request")
        query = prompt_builder(request)

        response = await agent.ainvoke({"messages": [("user", query)]})
        if isinstance(response, dict) and "messages" in response:   
            ai_messages = [msg for msg in response["messages"] if isinstance(msg, AIMessage)]
            output_text = "\n".join(msg.content for msg in ai_messages)
        else:
            output_text = str(response)

        if state_field == "attraction":
            return {"attraction": output_text}
        elif state_field == "hotel":
            return {"hotel": output_text}
        elif state_field == "weather":
            return {"weather": output_text}
        
        return state
    return call_agent

def attraction_query(agent) -> callable:
    return _make_query_handler(
        agent,
        lambda r: f"请搜索{r.city}的{'热门' if not r.preferences else '和'.join(r.preferences)}相关景点。\n",
        "attraction"
    )

def hotel_query(agent) -> callable:
    return _make_query_handler(
        agent,
        lambda r: f"请搜索{r.city}的{r.accommodation}相关酒店。\n",
        "hotel"
    )

def weather_query(agent) -> callable:
    return _make_query_handler(
        agent,
        lambda r: f"请查询{r.city}在{r.start_date}到{r.end_date}期间的天气情况。\n",
        "weather"
    )

def planner_query(agent) -> callable:
    async def call_agent(state: AgentState):
        request = state.get("request")
        query = f"""
请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:
**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 住宿: {request.accommodation}
- 偏好: {', '.join(request.preferences) if request.preferences else '无'}

**景点信息:**
{state["attraction"]}

**天气信息:**
{state["weather"]}

**酒店信息:**
{state["hotel"]}

**要求:**
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐
3. 每天推荐一个具体的酒店(从酒店信息中选择)
3. 考虑景点之间的距离和交通方式
4. 返回完整的JSON格式数据
5. 景点的经纬度坐标要真实准确
"""
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

        response = await agent.ainvoke({"messages": [("user", query)]})
        if isinstance(response, dict) and "messages" in response:   
            ai_messages = [msg for msg in response["messages"] if isinstance(msg, AIMessage)]
            output_text = "\n".join(msg.content for msg in ai_messages)
        else:
            output_text = str(response)

        return {"planner": output_text}

    return call_agent

def _parse_response(response: str, request: TripRequest) -> TripPlan:
    """
    解析Agent响应
    
    Args:
        response: Agent响应文本
        request: 原始请求
        
    Returns:
        旅行计划
    """
    try:
        # 尝试从响应中提取JSON
        # 查找JSON代码块
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        elif "```" in response:
            json_start = response.find("```") + 3
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        elif "{" in response and "}" in response:
            # 直接查找JSON对象
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]
        else:
            raise ValueError("响应中未找到JSON数据")
        
        # 解析JSON
        data = json.loads(json_str)
        
        # 转换为TripPlan对象
        trip_plan = TripPlan(**data)
        
        return trip_plan
        
    except Exception as e:
        print(f"⚠️  解析响应失败: {str(e)}")

class AgentState(TypedDict):
    attraction: Optional[str]
    hotel: Optional[str]
    weather: Optional[str]
    planner: Optional[str]
    request: TripRequest

async def main():
    mcp_tools = await get_mcp_tools()

    attraction_agent = await init_agent("attraction_agent", ATTRACTION_AGENT_PROMPT, mcp_tools)
    hotel_agent = await init_agent("hotel_agent", HOTEL_AGENT_PROMPT, mcp_tools)
    weather_agent = await init_agent("weather_agent", WEATHER_AGENT_PROMPT, mcp_tools)
    planner_agent = await init_agent("planner_agent", PLANNER_AGENT_PROMPT)

    builder = StateGraph(AgentState)

    builder.add_node("attraction_query", attraction_query(attraction_agent))
    builder.add_node("hotel_query", hotel_query(hotel_agent))
    builder.add_node("weather_query", weather_query(weather_agent))
    builder.add_node("planner_query", planner_query(planner_agent))
    builder.set_entry_point('attraction_query')

    builder.add_edge('attraction_query', 'hotel_query')
    builder.add_edge('hotel_query', 'weather_query')
    builder.add_edge('weather_query', 'planner_query')
    builder.add_edge('planner_query', END)

    graph = builder.compile()
    # print(graph.get_graph().draw_mermaid())

    # 生成一个TripRequest实例
    trip_request = TripRequest(
        city="北京",
        start_date="2026-01-19",
        end_date="2026-01-22",
        travel_days=3,
        transportation="公共交通",
        accommodation="经济型酒店",
        preferences=["历史文化", "美食"],
        free_text_input="希望多安排一些博物馆"
    )

    initial_state: AgentState = {
        "messages": [],
        "request": trip_request
    }
    
    final_state = await graph.ainvoke(initial_state)
    print(final_state["planner"])
    trip_plan = _parse_response(final_state["planner"], trip_request)
    print("tripplan:", trip_plan)

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(get_mcp_tools())
