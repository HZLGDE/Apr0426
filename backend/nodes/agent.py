import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain.agents import create_agent
from backend.tools.tools  import qtools
from backend.states.state import QuoteState
from backend.prompts.agent_prompt import AGENT_SYSTEM_PROMPT
from langchain_ollama import ChatOllama
from langgraph.types import Command
from langchain.messages import HumanMessage,AIMessage

class QuoteAgent:
    def __init__(self):
        self.llm = ChatOllama(model='mistral')
        self.agent = create_agent(
            model=self.llm,
            tools=qtools,
            system_prompt=AGENT_SYSTEM_PROMPT
        )
    
    async def run(self,state:QuoteState): 
        try:
            msgs = state.get('messages',None)
            # get last human message 
            def last_human(msgs):
                for m in reversed(msgs):
                    if isinstance(m,HumanMessage):
                        return m
                return HumanMessage(content='None')
            hmessage = last_human(msgs=msgs)
            response = await self.agent.ainvoke({'messages':[hmessage]})
            print("=="*20)
            print(response)
            print(f'\n')
            # get ai message
            def last_ai(response):
                for m in reversed(response):
                    if isinstance(m,AIMessage):
                        return m
                return AIMessage(content='None')
            rmessage = response['messages']
            aimess = last_ai(rmessage)
            return response
        except Exception as e:
            return {
                'messages':f'Error {e}'
            }

if __name__ == '__main__':
    import asyncio
    async def test():
        agent = QuoteAgent()
        state = QuoteState(
            messages=[HumanMessage(content='Im feeling really down today')]
        )
        result = await agent.run(state)
        for m in result['messages']:
            m.pretty_print()
    
    asyncio.run(test())