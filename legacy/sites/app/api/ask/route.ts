import {env} from "cloudflare:workers";
import {askRequest} from "../../../lib/service.mjs";
export function POST(request:Request){return askRequest(request,env)}
