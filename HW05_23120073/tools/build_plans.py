"""
Generator for the HW05 JMeter test plans (Load / Stress / Spike).

Workflow under test (mirrors frontend-admin/src/App.jsx exactly):
  1. POST /api/login                       (auth-heavy)
  2. fetchData(): GET /api/admin/users, /api/admin/orders,
     /api/products, /api/categories, /api/coupons   (read-heavy)
  3. POST /api/admin/import-products {products:[...]}  (transactional)
  4. fetchData() again (frontend refreshes after import)

Usage:
  python build_plans.py --date 20261121            # writes ../test_plans/*.jmx
  python build_plans.py --date 20261121 --smoke DIR # tiny smoke variants into DIR
"""
import argparse
import os
from xml.sax.saxutils import escape

STUDENT_ID = "23120073"
HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# Scenario profiles (reviewed by the student, see main_report.md section 3)
# --------------------------------------------------------------------------
# Each thread-group step: (label, threads, ramp_s, delay_s, duration_s)
SCENARIOS = {
    "Load": {
        "desc": "Load test: 20 concurrent admins, 60 s ramp-up, 10 min steady state.",
        "steps": [("Load - 20 VU steady", "${__P(threads,20)}", "${__P(rampup,60)}", "0", "${__P(duration,600)}")],
        "think_login": (2000, 3000),   # Uniform: 2-5 s before each new session
        "think_import": (3000, 5000),  # Uniform: 3-8 s reading list + choosing CSV
        "listener": ("StatVisualizer", "Aggregate Report"),
    },
    "Stress": {
        "desc": "Stress test: stepped load 10 -> 25 -> 50 -> 100 -> 200 VU, 2 min per step, reduced think-time.",
        "steps": [
            ("Stress - step 1 (+10 = 10 VU)", "10", "20", "0", "600"),
            ("Stress - step 2 (+15 = 25 VU)", "15", "20", "120", "480"),
            ("Stress - step 3 (+25 = 50 VU)", "25", "20", "240", "360"),
            ("Stress - step 4 (+50 = 100 VU)", "50", "20", "360", "240"),
            ("Stress - step 5 (+100 = 200 VU)", "100", "30", "480", "120"),
        ],
        "think_login": (500, 1000),    # 0.5-1.5 s: push beyond normal usage
        "think_import": (500, 1000),
        "listener": ("SummaryReport", "Summary Report"),
    },
    "Spike": {
        "desc": "Spike test: 10 VU baseline, +140 VU within 5 s at t=120 s held 60 s, then recovery.",
        "steps": [
            ("Spike - baseline 10 VU", "10", "10", "0", "360"),
            ("Spike - burst +140 VU", "140", "5", "120", "65"),
        ],
        "think_login": (2000, 3000),
        "think_import": (3000, 5000),
        "listener": ("RespTimeGraphVisualizer", "Response Time Graph"),
    },
}

SMOKE_STEPS = {
    "Load": [("Load - smoke", "2", "2", "0", "20")],
    "Stress": [("Stress - smoke 1", "2", "2", "0", "20"), ("Stress - smoke 2", "2", "2", "5", "15")],
    "Spike": [("Spike - smoke base", "1", "1", "0", "20"), ("Spike - smoke burst", "3", "1", "5", "10")],
}

_uid = [0]


def uid():
    _uid[0] += 1
    return str(_uid[0])


def s(name, value):
    return f'<stringProp name="{name}">{escape(str(value))}</stringProp>'


def b(name, value):
    return f'<boolProp name="{name}">{"true" if value else "false"}</boolProp>'


def node(xml, children=""):
    """Element followed by its hashTree."""
    return f"{xml}\n<hashTree>{children}</hashTree>\n"


# --------------------------------------------------------------------------
# Element builders
# --------------------------------------------------------------------------
def arguments(pairs):
    items = "".join(
        f'<elementProp name="{escape(k)}" elementType="Argument">{s("Argument.name", k)}{s("Argument.value", v)}{s("Argument.metadata", "=")}</elementProp>'
        for k, v in pairs
    )
    return items


def http_sampler(label, method, path, body=None):
    if body is None:
        args = '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables"><collectionProp name="Arguments.arguments"/></elementProp>'
        raw = b("HTTPSampler.postBodyRaw", False)
    else:
        args = (
            '<elementProp name="HTTPsampler.Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments">'
            f'<elementProp name="" elementType="HTTPArgument">{b("HTTPArgument.always_encode", False)}{s("Argument.value", body)}{s("Argument.metadata", "=")}</elementProp>'
            "</collectionProp></elementProp>"
        )
        raw = b("HTTPSampler.postBodyRaw", True)
    return (
        f'<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{escape(label)}">'
        f"{raw}{args}{s('HTTPSampler.path', path)}{s('HTTPSampler.method', method)}"
        f"{s('HTTPSampler.contentEncoding', 'UTF-8')}{b('HTTPSampler.follow_redirects', True)}"
        f"{b('HTTPSampler.auto_redirects', False)}{b('HTTPSampler.use_keepalive', True)}"
        f"{b('HTTPSampler.DO_MULTIPART_POST', False)}</HTTPSamplerProxy>"
    )


def assert_code(code="200"):
    return node(
        f'<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Assert HTTP {code}">'
        f'<collectionProp name="Asserion.test_strings">{s(uid(), code)}</collectionProp>'
        f"{s('Assertion.custom_message', 'Expected HTTP ' + code)}{s('Assertion.test_field', 'Assertion.response_code')}"
        f"{b('Assertion.assume_success', False)}<intProp name=\"Assertion.test_type\">8</intProp></ResponseAssertion>"
    )


def assert_json(label, path, expected=None):
    return node(
        f'<JSONPathAssertion guiclass="JSONPathAssertionGui" testclass="JSONPathAssertion" testname="{escape(label)}">'
        f"{s('JSON_PATH', path)}{s('EXPECTED_VALUE', expected or '')}{b('JSONVALIDATION', expected is not None)}"
        f"{b('EXPECT_NULL', False)}{b('INVERT', False)}{b('ISREGEX', False)}</JSONPathAssertion>"
    )


def assert_duration():
    return node(
        '<DurationAssertion guiclass="DurationAssertionGui" testclass="DurationAssertion" testname="Assert duration &lt;= ${MAX_RT_MS} ms">'
        f"{s('DurationAssertion.duration', '${MAX_RT_MS}')}</DurationAssertion>"
    )


def think(label, const_ms, range_ms):
    return node(
        f'<UniformRandomTimer guiclass="UniformRandomTimerGui" testclass="UniformRandomTimer" testname="{escape(label)}">'
        f"{s('ConstantTimer.delay', const_ms)}{s('RandomTimer.range', range_ms)}</UniformRandomTimer>"
    )


def json_extractor(var, path, default):
    return node(
        f'<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract {var}">'
        f"{s('JSONPostProcessor.referenceNames', var)}{s('JSONPostProcessor.jsonPathExprs', path)}"
        f"{s('JSONPostProcessor.match_numbers', '1')}{s('JSONPostProcessor.defaultValues', default)}</JSONPostProcessor>"
    )


def jsr223(tag, label, script):
    gui = "TestBeanGUI"
    return node(
        f'<{tag} guiclass="{gui}" testclass="{tag}" testname="{escape(label)}">'
        f"{s('scriptLanguage', 'groovy')}{s('parameters', '')}{s('filename', '')}{s('cacheKey', 'true')}{s('script', script)}</{tag}>"
    )


def header_manager(label, headers):
    items = "".join(
        f'<elementProp name="" elementType="Header">{s("Header.name", k)}{s("Header.value", v)}</elementProp>' for k, v in headers
    )
    return node(
        f'<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="{escape(label)}"><collectionProp name="HeaderManager.headers">{items}</collectionProp></HeaderManager>'
    )


SAVE_CONFIG = (
    "<objProp><name>saveConfig</name><value class=\"SampleSaveConfiguration\">"
    "<time>true</time><latency>true</latency><timestamp>true</timestamp><success>true</success><label>true</label>"
    "<code>true</code><message>true</message><threadName>true</threadName><dataType>true</dataType><encoding>false</encoding>"
    "<assertions>true</assertions><subresults>true</subresults><responseData>false</responseData><samplerData>false</samplerData>"
    "<xml>false</xml><fieldNames>true</fieldNames><responseHeaders>false</responseHeaders><requestHeaders>false</requestHeaders>"
    "<responseDataOnError>false</responseDataOnError><saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>"
    "<assertionsResultsToSave>0</assertionsResultsToSave><bytes>true</bytes><sentBytes>true</sentBytes><url>true</url>"
    "<threadCounts>true</threadCounts><idleTime>true</idleTime><connectTime>true</connectTime></value></objProp>"
)


def listener(gui, label, jtl_filename=""):
    return node(
        f'<ResultCollector guiclass="{gui}" testclass="ResultCollector" testname="{escape(label)}">'
        f"{b('ResultCollector.error_logging', False)}{SAVE_CONFIG}{s('filename', jtl_filename)}</ResultCollector>"
    )


# --------------------------------------------------------------------------
# Groovy scripts
# --------------------------------------------------------------------------
BUILD_BATCH = r"""// Data-driven import payload: takes the next BATCH_SIZE rows of products_import.csv
// (shared cursor across all threads) and builds the same JSON the admin frontend sends.
import groovy.json.JsonOutput
import java.util.concurrent.atomic.AtomicInteger
import org.apache.jmeter.services.FileServer

def rows = props.get('HW05_IMPORT_ROWS')
if (rows == null) {
    synchronized (props) {
        rows = props.get('HW05_IMPORT_ROWS')
        if (rows == null) {
            def f = new File(FileServer.getFileServer().getBaseDir(), vars.get('IMPORT_CSV'))
            def lines = f.readLines('UTF-8').findAll { it.trim() }
            def headers = lines[0].replace('\uFEFF', '').split(',').collect { it.trim() }
            rows = lines.drop(1).collect { line ->
                def v = line.split(',', -1).collect { it.trim() }
                def m = [:]
                headers.eachWithIndex { h, i -> m[h] = i < v.size() ? v[i] : '' }
                m
            }
            props.put('HW05_IMPORT_ROWS', rows)
            props.put('HW05_IMPORT_CURSOR', new AtomicInteger(0))
            log.info("HW05: loaded ${rows.size()} import rows from ${f}")
        }
    }
}
AtomicInteger cursor = props.get('HW05_IMPORT_CURSOR')
int batch = vars.get('BATCH_SIZE') as int
def products = (0..<batch).collect {
    def r = rows[cursor.getAndIncrement() % rows.size()]
    // same mapping as frontend-admin App.jsx (price kept as string, category_id parsed to int)
    [name: r.name ?: '', price: r.price ?: 0, description: r.description ?: '',
     imageUrl: r.imageUrl ?: '', category_id: (r.category_id ?: '1') as int]
}
vars.put('importBody', JsonOutput.toJson([products: products]))
"""

COUNT_PRODUCTS = r"""// Records how many products exist (GET /api/products is not paginated, so payload grows with imports)
def n = new groovy.json.JsonSlurper().parse(prev.getResponseData()).size()
log.info("HW05: ${prev.getSampleLabel()} product count = ${n}, payload = ${prev.getBodySizeAsLong()} bytes")
"""


# --------------------------------------------------------------------------
# Workflow (4 core steps: Login -> View Product List -> Import CSV -> Refresh Product List)
# --------------------------------------------------------------------------
def fetch_products(suffix, step_no):
    """Calls GET /api/products to view the product list."""
    label = f"{step_no:02d}_Read_GET_products{suffix}"
    kids = (
        assert_code()
        + assert_duration()
        + assert_json("Assert list not empty ($[0].id exists)", "$[0].id")
    )
    return node(http_sampler(label, "GET", "/api/products"), kids)


def workflow(sc):
    tl, ti = sc["think_login"], sc["think_import"]
    login = node(
        http_sampler("01_Auth_POST_login", "POST", "/api/login", '{"email":"${email}","password":"${password}"}'),
        think(f"Think {tl[0]/1000:g}-{(tl[0]+tl[1])/1000:g} s (new admin session)", *tl)
        + assert_code()
        + assert_json("Assert role == admin", "$.user.role", "admin")
        + assert_duration()
        + json_extractor("token", "$.token", "NOTFOUND"),
    )
    import_sampler = node(
        http_sampler("03_Txn_POST_import_products", "POST", "/api/admin/import-products", "${importBody}"),
        think(f"Think {ti[0]/1000:g}-{(ti[0]+ti[1])/1000:g} s (review list, choose CSV)", *ti)
        + jsr223("JSR223PreProcessor", "Build JSON batch from products_import.csv", BUILD_BATCH)
        + assert_code()
        + assert_json("Assert inserted == BATCH_SIZE", "$.inserted", "${BATCH_SIZE}")
        + assert_json("Assert no row errors", "$.errors", "[]")
        + assert_duration(),
    )
    import_ctrl = node(
        '<ThroughputController guiclass="ThroughputControllerGui" testclass="ThroughputController" testname="Import CSV in ${IMPORT_PCT}% of sessions">'
        '<intProp name="ThroughputController.style">1</intProp>'
        f"{b('ThroughputController.perThread', False)}"
        '<intProp name="ThroughputController.maxThroughput">1</intProp>'
        f"{s('ThroughputController.percentThroughput', '${IMPORT_PCT}')}</ThroughputController>",
        import_sampler + fetch_products("_after_import", 4),
    )
    authed = node(
        '<IfController guiclass="IfControllerPanel" testclass="IfController" testname="If login OK (token found, account not locked)">'
        f"{s('IfController.condition', '${__groovy(vars.get(\"token\") != \"NOTFOUND\")}')}"
        f"{b('IfController.evaluateAll', False)}{b('IfController.useExpression', True)}</IfController>",
        header_manager("Authorization: Bearer ${token}", [("Authorization", "Bearer ${token}")])
        + fetch_products("", 2)
        + import_ctrl,
    )
    return login + authed


def thread_group(label, threads, ramp, delay, duration, body):
    return node(
        f'<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="{escape(label)}">'
        f"{s('ThreadGroup.on_sample_error', 'continue')}"
        '<elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">'
        f"{b('LoopController.continue_forever', False)}<intProp name=\"LoopController.loops\">-1</intProp></elementProp>"
        f"{s('ThreadGroup.num_threads', threads)}{s('ThreadGroup.ramp_time', ramp)}{b('ThreadGroup.scheduler', True)}"
        f"{s('ThreadGroup.duration', duration)}{s('ThreadGroup.delay', delay)}{b('ThreadGroup.same_user_on_next_iteration', True)}"
        "</ThreadGroup>",
        body,
    )


def special_group(tag, gui, label, body, on_error):
    return node(
        f'<{tag} guiclass="{gui}" testclass="{tag}" testname="{escape(label)}">'
        f"{s('ThreadGroup.on_sample_error', on_error)}"
        '<elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">'
        f"{b('LoopController.continue_forever', False)}<intProp name=\"LoopController.loops\">1</intProp></elementProp>"
        f"{s('ThreadGroup.num_threads', '1')}{s('ThreadGroup.ramp_time', '1')}{b('ThreadGroup.scheduler', False)}"
        f"{s('ThreadGroup.duration', '')}{s('ThreadGroup.delay', '')}</{tag}>",
        body,
    )


def preflight():
    """setUp: fail fast if admin is locked (403) -> restart backend before running."""
    login = node(
        http_sampler("SETUP_preflight_login", "POST", "/api/login", '{"email":"${email}","password":"${password}"}'),
        assert_code() + json_extractor("token", "$.token", "NOTFOUND"),
    )
    count = node(
        http_sampler("SETUP_product_count", "GET", "/api/products"),
        assert_code() + jsr223("JSR223PostProcessor", "Log product count (start)", COUNT_PRODUCTS),
    )
    return special_group(
        "SetupThreadGroup", "SetupThreadGroupGui",
        "setUp - preflight (stop test if admin locked; reset = restart node server.js)",
        login + count, "stoptestnow",
    )


def teardown():
    count = node(
        http_sampler("TEARDOWN_product_count", "GET", "/api/products"),
        assert_code() + jsr223("JSR223PostProcessor", "Log product count (end)", COUNT_PRODUCTS),
    )
    return special_group("PostThreadGroup", "PostThreadGroupGui", "tearDown - final product count", count, "continue")


def build(scenario, date, smoke=False):
    sc = SCENARIOS[scenario]
    name = f"{STUDENT_ID}_{scenario}_{date}"
    steps = SMOKE_STEPS[scenario] if smoke else sc["steps"]
    plan_vars = [
        ("HOST", "${__P(host,localhost)}"),
        ("PORT", "${__P(port,3000)}"),
        ("BATCH_SIZE", "${__P(batch,5)}"),
        ("IMPORT_PCT", "${__P(import_pct,20)}"),
        ("MAX_RT_MS", "${__P(max_rt,5000)}"),
        ("IMPORT_CSV", "../data/products_import.csv"),
    ]
    test_plan = (
        f'<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{name}">'
        f"{s('TestPlan.comments', sc['desc'] + ' Workflow: admin login -> view product list (GET /api/products) -> import CSV -> refresh product list. SUT: eshop-sut backend :3000, client: frontend-admin.')}"
        f"{b('TestPlan.functional_mode', False)}{b('TestPlan.serialize_threadgroups', False)}{b('TestPlan.tearDown_on_shutdown', True)}"
        '<elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">'
        f'<collectionProp name="Arguments.arguments">{arguments(plan_vars)}</collectionProp></elementProp>'
        f"{s('TestPlan.user_define_classpath', '')}</TestPlan>"
    )
    defaults = node(
        '<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults (backend :3000)">'
        '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables"><collectionProp name="Arguments.arguments"/></elementProp>'
        f"{s('HTTPSampler.domain', '${HOST}')}{s('HTTPSampler.port', '${PORT}')}{s('HTTPSampler.protocol', 'http')}"
        f"{s('HTTPSampler.connect_timeout', '5000')}{s('HTTPSampler.response_timeout', '30000')}"
        f"{s('HTTPSampler.implementation', 'HttpClient4')}</ConfigTestElement>"
    )
    headers = header_manager(
        "Headers like frontend-admin (JSON, Origin :5174)",
        [("Content-Type", "application/json"), ("Accept", "application/json, text/plain, */*"), ("Origin", "http://localhost:5174")],
    )
    csv = node(
        '<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="CSV Data Set - admin_credentials.csv">'
        f"{s('filename', '../data/admin_credentials.csv')}{s('fileEncoding', 'UTF-8')}{s('variableNames', 'email,password')}"
        f"{b('ignoreFirstLine', True)}{s('delimiter', ',')}{b('quotedData', False)}{b('recycle', True)}"
        f"{b('stopThread', False)}{s('shareMode', 'shareMode.all')}</CSVDataSet>"
    )
    jtl_default = "" if smoke else os.path.normpath(os.path.join(HERE, "..", "results", f"{STUDENT_ID}_{scenario}_20261122.jtl"))
    groups = "".join(thread_group(lab, t, r, d, du, workflow(sc)) for lab, t, r, d, du in steps)
    body = defaults + headers + csv + preflight() + groups + teardown() + listener(*sc["listener"], jtl_default)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">\n<hashTree>\n'
        + node(test_plan, body)
        + "</hashTree>\n</jmeterTestPlan>\n"
    )
    return name, xml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYYMMDD of the run")
    ap.add_argument("--smoke", help="output dir for tiny smoke-test variants")
    a = ap.parse_args()
    out = a.smoke or os.path.join(HERE, "..", "test_plans")
    os.makedirs(out, exist_ok=True)
    for sc in SCENARIOS:
        name, xml = build(sc, a.date, smoke=bool(a.smoke))
        path = os.path.join(out, name + ".jmx")
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
        print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
