import os
from dotenv import load_dotenv

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from braintrust.otel import BraintrustSpanProcessor

AzureMonitorTraceExporter = None
AzureMonitorDistro = None
try:
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter as _AZ_Exporter
    AzureMonitorTraceExporter = _AZ_Exporter
except Exception:
    pass

try:
    from azure.monitor.opentelemetry import configure_azure_monitor as _AZ_Distro
    AzureMonitorDistro = _AZ_Distro
except Exception:
    pass


def setup_tracing():
    load_dotenv()
    project_name = os.getenv("PROJECT_NAME", "LocalDevProject")
    os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{project_name}")

    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    provider.add_span_processor(
        BraintrustSpanProcessor(api_key=os.getenv("BRAINTRUST_API_KEY", ""))
    )

    conn = os.getenv("AZURE_MONITOR_CONNECTION_STRING", "")
    if conn and AzureMonitorTraceExporter is not None:
        provider.add_span_processor(
            BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=conn))
        )

    return trace.get_tracer(__name__)


if __name__ == "__main__":
    tracer = setup_tracing()
    with tracer.start_as_current_span("sanity-span"):
        pass
    print("OTel configured: Braintrust + (optional) Azure Monitor.")
