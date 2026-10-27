import os,socket,sys,time
pid=int(sys.argv[1])
for _ in range(180):
 os.kill(pid,0)
 try:
  with socket.create_connection(("127.0.0.1",int(os.getenv("PORT","8093"))),timeout=2):break
 except OSError:time.sleep(5)
else:raise SystemExit("FACT server readiness timeout")
