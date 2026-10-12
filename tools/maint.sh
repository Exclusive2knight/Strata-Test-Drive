#!/bin/sh
# Maintenance screen on the live site.
#   sh tools/maint.sh on ["message"]   -> players see "Under maintenance" (auto-expires after 40 minutes)
#   sh tools/maint.sh off VERSION       -> maintenance off; players on an older version get a "Reload" prompt
cd "$(dirname "$0")/.."
if [ "$1" = on ]; then
  python3 -c "import json,sys,time;d=json.load(open('maint.json'));d.update(on=True,until=int(time.time()*1000)+40*60*1000,msg=sys.argv[1] if len(sys.argv)>1 else '');json.dump(d,open('maint.json','w'))" "$2"
  git add maint.json && git commit -qm "Maintenance on" && git push -q origin main
else
  python3 -c "import json,sys;d=json.load(open('maint.json'));d.update(on=False,msg='');d.pop('until',None);d['ver']=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1] else d.get('ver',0);json.dump(d,open('maint.json','w'))" "$2"
fi
