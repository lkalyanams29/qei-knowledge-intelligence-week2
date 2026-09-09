"""Make an AI-narrated screenshot walkthrough, not a continuous live recording.

Inputs are actual browser screenshots captured during the local app walkthrough.
Use --ffmpeg with an installed FFmpeg binary. Windows SAPI supplies narration.
"""
from pathlib import Path
import argparse,json,subprocess,wave
ROOT=Path(__file__).resolve().parents[1]
scenes=[
 ("01-home","This is an AI-narrated screenshot walkthrough of Q E I Knowledge Intelligence, the separate Week Two project. The screenshots were captured while querying the working local application. For the final assignment, use the included guide to record a continuous live demonstration. The app helps quality engineers inspect test history and project context with source provenance. It does not claim live access to enterprise systems."),
 ("02-run-answer","Here a question about run zero zero zero zero one goes through the real retrieval service. Python ingests the approved corpus, creates document chunks, and fits ninety six dimensional classical L S A embeddings. The server combines keyword and vector retrieval, follows recorded graph links, and selects evidence within project scope. The configured local language model selects quotations rather than inventing new factual prose."),
 ("03-answer-detail","The answer lists the four test identifiers recorded in this run. Additional records show individual test histories. Citation numbers point to retrieved evidence with source IDs, authority and dates. This is a frozen sample snapshot, so the answer describes observed history rather than current production behavior."),
 ("04-source-detail","Opening the retrieved excerpt reveals the underlying run summary and every contributing CSV row. The original source link goes to the approved dataset in the separate GitHub repository. A test run proves that results were observed; it does not by itself prove acceptance criteria coverage."),
 ("05-refusal","The missing Jira question illustrates safe refusal. Acceptance criteria for this issue were never supplied, so the assistant reports insufficient evidence. It does not fill the gap with a plausible requirement. Current status questions also refuse when only dated execution records are available."),
 ("06-mentor","Mentor Mode uses the same retrieval pipeline. For C X E, the supplied design notes support a user journey testing strategy. The learning path adds an exercise and knowledge check, while identifying missing implementation and requirement evidence. The design brief is labeled with its own authority and unknown update date."),
 ("07-corpus","The corpus view makes the data boundary visible. The approved CSV has two thousand sixty three results, one hundred forty four test IDs and ninety six runs. It combines with six design profiles and four public documentation summaries to form two hundred fifty four records. Jira, SharePoint and Bitbucket exports have not been imported. Public documentation about a tool does not mean enterprise access is connected."),
 ("08-graph","The graph contains two hundred fifty four nodes and four thousand two hundred seventy directed links. These links come from recorded test and run identifiers, not similarity guesses. A selected run exposes its recorded test cases, and those tests link back to their observed runs."),
 ("09-evaluation","Twenty five authored development questions test answerability, expected sources and refusal. Exact quotation support was one hundred percent on this development set, but semantic faithfulness remains unmeasured. On ten relationship queries, graph assisted recall was fifty seven point one percent versus forty nine point two percent for the vector baseline. Codex helped build the pipeline, tests, UI and documentation. Browser testing exposed a relevant-source but wrong-excerpt defect, which was corrected with a regression test. The latest local model evaluation had seventeen validated model responses and eight pre-generation refusals. Nineteen unit tests and the production build passed. Next steps are independent human evaluation, authorized enterprise exports, a native Google Doc and the final live recording.")
]
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--ffmpeg",required=True);args=parser.parse_args()
 work=ROOT/"work/walkthrough";work.mkdir(parents=True,exist_ok=True)
 out=ROOT/"demo";out.mkdir(exist_ok=True)
 durations=[];parts=[]
 for i,(name,text) in enumerate(scenes):
  screenshot=ROOT/"demo/screens"/(name+".png")
  narration=work/(name+".txt");narration.write_text(text,encoding="utf-8")
  wav=work/(name+".wav");mp4=work/(name+".mp4")
  subprocess.run(["C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe","-NoProfile","-File",str(ROOT/"scripts/render_narration.ps1"),"-TextPath",str(narration),"-OutputPath",str(wav)],check=True)
  with wave.open(str(wav)) as audio: duration=audio.getnframes()/audio.getframerate()+.3
  durations.append(duration)
  subprocess.run([args.ffmpeg,"-y","-loop","1","-i",str(screenshot),"-i",str(wav),"-t",str(duration),"-r","24","-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p","-c:v","libx264","-preset","fast","-crf","24","-c:a","aac","-b:a","128k","-shortest",str(mp4)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  parts.append(mp4)
 manifest=work/"parts.txt";manifest.write_text("\n".join("file '"+p.as_posix()+"'" for p in parts),encoding="utf-8")
 final=out/"QEI_Week2_Walkthrough_Draft.mp4"
 subprocess.run([args.ffmpeg,"-y","-f","concat","-safe","0","-i",str(manifest),"-c","copy",str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 metadata={"kind":"AI-narrated edited screenshot walkthrough; not a continuous live recording","seconds":round(sum(durations),2),"bytes":final.stat().st_size,"scenes":[{"capture":name,"narration":text,"seconds":round(d,2)} for (name,text),d in zip(scenes,durations)]}
 (out/"walkthrough-manifest.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
 if metadata["seconds"]>300:raise ValueError("Video exceeds five minutes")
 print(json.dumps({k:v for k,v in metadata.items() if k!="scenes"}))
if __name__=="__main__":main()
