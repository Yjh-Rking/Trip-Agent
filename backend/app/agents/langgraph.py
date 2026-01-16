import os
import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from app.models.schemas import TripRequest
from langgraph.graph import END, StateGraph
from langchain_core.messages import AnyMessage, AIMessage
from typing import Annotated, TypedDict
import operator
from .prompt import ATTRACTION_AGENT_PROMPT, WEATHER_AGENT_PROMPT, HOTEL_AGENT_PROMPT

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

def _make_query_handler(agent, prompt_builder):
    async def call_agent(state: AgentState):
        request = state.get("request")
        query = prompt_builder(request)

        response = await agent.ainvoke({"messages": [("user", query)]})
        if isinstance(response, dict) and "messages" in response:   
            ai_messages = [msg for msg in response["messages"] if isinstance(msg, AIMessage)]
            output_text = "\n".join(msg.content for msg in ai_messages)
        else:
            output_text = str(response)

        return {"messages": state["messages"] + [AIMessage(content=output_text)], "action": None}

    return call_agent

def attraction_query(agent):
    return _make_query_handler(
        agent,
        lambda r: f"请搜索{r.city}的{'热门' if not r.preferences else ','.join(r.preferences)}相关景点。\n"
    )

def hotel_query(agent):
    return _make_query_handler(
        agent,
        lambda r: f"请搜索{r.city}的{r.accommodation}相关酒店。\n" 
    )

def weather_query(agent):
    return _make_query_handler(
        agent,
        lambda r: f"请查询{r.city}在{r.start_date}到{r.end_date}期间的天气情况。\n"
    )

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    request: TripRequest

async def main():
    mcp_tools = await get_mcp_tools()

    attraction_agent = await init_agent("attraction_agent", ATTRACTION_AGENT_PROMPT, mcp_tools)
    hotel_agent = await init_agent("hotel_agent", HOTEL_AGENT_PROMPT, mcp_tools)
    weather_agent = await init_agent("weather_agent", WEATHER_AGENT_PROMPT, mcp_tools)

    builder = StateGraph(AgentState)

    builder.add_node("attraction_query", attraction_query(attraction_agent))
    builder.add_node("hotel_query", hotel_query(hotel_agent))
    builder.add_node("weather_query", weather_query(weather_agent))
    builder.set_entry_point('attraction_query')
    builder.add_edge('attraction_query', 'hotel_query')
    builder.add_edge('hotel_query', 'weather_query')
    builder.add_edge('weather_query', END)

    graph = builder.compile()
    print(graph.get_graph().draw_mermaid())

    # 生成一个TripRequest实例
    trip_request = TripRequest(
        city="北京",
        start_date="2025-06-01",
        end_date="2025-06-03",
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
    for message in final_state["messages"]:
        print(f"{type(message).__name__}: {message.content}")

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(get_mcp_tools())
