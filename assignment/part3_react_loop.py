def get_stock_price(ticker_symbol: str) -> dict:
    return {"price": 175.50, "volume": 50000000}

def calculate_pe_ratio(price: float, earnings_per_share: float) -> float:
    return price / earnings_per_share

class ReActAgent:
    def __init__(self):
        self.tools = {
            "get_stock_price": get_stock_price,
            "calculate_pe_ratio": calculate_pe_ratio
        }
        self.step = 0

    def run(self, query: str):
        print(f"Question: {query}\n")

        # Hardcoded reasoning trace to simulate LLM logic for the example
        trace = [
            {
                "thought": "I need to calculate the P/E ratio for AAPL. I have the EPS ($6.50) but I don't know the current stock price. I will use the `get_stock_price` tool to find the current price of AAPL.",
                "tool_call": {"name": "get_stock_price", "args": {"ticker_symbol": "AAPL"}}
            },
            {
                "thought": "I now have the current price of AAPL ($175.50) and the EPS ($6.50). I can use the `calculate_pe_ratio` tool to find the P/E ratio.",
                "tool_call": {"name": "calculate_pe_ratio", "args": {"price": 175.50, "earnings_per_share": 6.50}}
            },
            {
                "thought": "I have the calculated P/E ratio of 27.0. I can now provide the final answer to the user.",
                "tool_call": None,
                "final_answer": "The P/E ratio for AAPL is 27.0, based on its current stock price of $175.50 and an EPS of $6.50."
            }
        ]

        for step in trace:
            print(f"Thought: {step['thought']}")
            if step["tool_call"]:
                tool_name = step["tool_call"]["name"]
                args = step["tool_call"]["args"]
                print(f"Action: {tool_name}(**{args})")

                # Execute tool
                func = self.tools[tool_name]
                observation = func(**args)
                print(f"Observation: {observation}\n")
            else:
                print(f"Final Answer: {step['final_answer']}\n")

agent = ReActAgent()
agent.run("What is the P/E ratio for AAPL if its current EPS is $6.50?")
