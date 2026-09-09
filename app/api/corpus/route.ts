import {env} from "cloudflare:workers";
import {corpusRequest} from "../../../lib/service.mjs";
export function GET(request:Request){return corpusRequest(request,env)}
