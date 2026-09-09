import {spawn} from "node:child_process";
import {fileURLToPath} from "node:url";
const child=spawn(process.execPath,[fileURLToPath(new URL("../node_modules/vinext/dist/cli.js",import.meta.url)),...process.argv.slice(2)],{stdio:"inherit",env:{...process.env,WRANGLER_LOG_PATH:".wrangler/wrangler.log",WRANGLER_SEND_METRICS:"false"}});
child.on("exit",code=>process.exit(code??1));
