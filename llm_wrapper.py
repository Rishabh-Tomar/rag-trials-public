from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
)
from llama_index.experimental.query_engine.pandas import (
    PandasInstructionParser,
)
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

class llm:
    def __init__(
        self,
        model,
        api_key,
        df,
        ):
        self.df = df
        self.qp = None
        self.model = model
        self.api_key = api_key
        
        
        self.instruction_str = (
        "1. Convert the query to executable Python code using Pandas.\n"
        "2. The final line of code should be a Python expression that can be called with the `eval()` function.\n"
        "3. The code should represent a solution to the query.\n"
        "4. PRINT ONLY THE EXPRESSION.\n"
        "5. Do not quote the expression.\n"
        )

        self.pandas_prompt_str = (
            "You are working with a pandas dataframe in Python.\n"
            "The name of the dataframe is `df`.\n"
            "This is the result of `print(df.head())`:\n"
            "{df_str}\n\n"
            "Follow these instructions:\n"
            "{instruction_str}\n"
            "Query: {query_str}\n\n"
            "Expression:"
        )
        self.response_synthesis_prompt_str = (
            "Given an input question, synthesize a response from the query results.\n"
            "Query: {query_str}\n\n"
            "Pandas Instructions (optional):\n{pandas_instructions}\n\n"
            "Pandas Output: {pandas_output}\n\n"
            "Response: "
        )
        
    def _build_prompts_and_llm(self):
        self.pandas_prompt = PromptTemplate(self.pandas_prompt_str).partial_format(
            instruction_str=self.instruction_str, df_str=self.df.head(5)
        )
        self.pandas_output_parser = PandasInstructionParser(self.df)
        self.response_synthesis_prompt = PromptTemplate(self.response_synthesis_prompt_str)
        self.llm = OpenAI(model=self.model, api_key=self.api_key)
        
    def _build_query_pipeline(self):
        self._build_prompts_and_llm()
        self.qp = QP(
            modules={
                "input": InputComponent(),
                "pandas_prompt": self.pandas_prompt,
                "llm1": self.llm,
                "pandas_output_parser": self.pandas_output_parser,
                "response_synthesis_prompt": self.response_synthesis_prompt,
                "llm2": self.llm,
            },
            verbose=True,
        )
        self.qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"])
        self.qp.add_links(
            [
                Link("input", "response_synthesis_prompt", dest_key="query_str"),
                Link("llm1", "response_synthesis_prompt", dest_key="pandas_instructions"),
                Link(
                    "pandas_output_parser",
                    "response_synthesis_prompt",
                    dest_key="pandas_output",
                ),
            ]
        )
        # add link from response synthesis prompt to llm2
        self.qp.add_link("response_synthesis_prompt", "llm2")

    def run_query(self, query):
        self._build_query_pipeline()
        response = self.qp.run(
            query_str=query,
        )

        return response.message.content