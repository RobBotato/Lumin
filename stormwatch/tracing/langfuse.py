from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, LLM_MODEL


_langfuse = None


def get_langfuse():
    global _langfuse
    if _langfuse is None and LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        from langfuse import Langfuse
        _langfuse = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
        )
    return _langfuse


class Trace:
    def __init__(self, name: str = "risk-assessment"):
        self.name = name
        self.lf = get_langfuse()
        if self.lf:
            self.trace_id = self.lf.create_trace_id()
        else:
            self.trace_id = "no-trace"
        self.observations: list = []

    def span(self, name: str, input_data=None, output_data=None):
        if self.lf:
            try:
                from langfuse.types import TraceContext
                obs = self.lf.start_observation(
                    trace_context=TraceContext(trace_id=self.trace_id),
                    name=name,
                    as_type="span",
                    input=input_data,
                    output=output_data,
                )
                self.observations.append(obs)
                return obs
            except Exception as e:
                print(f"  Langfuse span error: {e}")
        return None

    def generation(self, name: str, model: str = "", input_data=None, output_data=None):
        if self.lf:
            try:
                from langfuse.types import TraceContext
                obs = self.lf.start_observation(
                    trace_context=TraceContext(trace_id=self.trace_id),
                    name=name,
                    as_type="generation",
                    model=model or LLM_MODEL,
                    input=input_data,
                    output=output_data,
                )
                self.observations.append(obs)
                return obs
            except Exception as e:
                print(f"  Langfuse generation error: {e}")
        return None

    def end(self):
        if self.lf:
            for obs in self.observations:
                try:
                    obs.end()
                except Exception:
                    pass
            self.lf.flush()

    @property
    def id(self) -> str:
        return self.trace_id


class NoopTrace:
    def span(self, *args, **kwargs):
        return None
    def generation(self, *args, **kwargs):
        return None
    def end(self):
        pass
    @property
    def id(self) -> str:
        return "no-trace"


def create_trace(name: str = "risk-assessment"):
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        return Trace(name)
    return NoopTrace()
