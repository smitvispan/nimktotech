#!/bin/bash
source /home/deep/business-directory/venv/bin/activate
pkill -f "python.*app.py" 2>/dev/null
sleep 1
python /home/deep/business-directory/app.py &
sleep 5

# Login
curl -s -c /tmp/tc_sh.txt -X POST http://127.0.0.1:8000/login -d "username=admin&password=admin123" -o /dev/null

# Test
echo "=== Bulk Scrape ==="
START=$(date +%s)
curl -s --max-time 25 "http://127.0.0.1:8000/api/bulk-scrape?city=Rajkot&type=Hardware" -b /tmp/tc_sh.txt > /tmp/bs_sh.json
echo "Time: $(($(date +%s)-START))s"

python3 -c "
import json
d=json.load(open('/tmp/bs_sh.json'))
print(f'Total: {len(d)}')
fe=sum(1 for b in d if b.get('emails'))
fl=sum(1 for b in d if b.get('linkedin'))
fp=sum(1 for b in d if b.get('phones'))
fo=sum(1 for b in d if b.get('owner_name'))
print(f'Emails: {fe}  LinkedIn: {fl}  Phones: {fp}  Owner: {fo}')
for b in d:
    li=','.join(b['linkedin'])[:35] if b.get('linkedin') else '-'
    ow=b.get('owner_name','') or '-'
    ph=','.join(b['phones']) if b.get('phones') else '-'
    em=','.join(b['emails']) if b.get('emails') else '-'
    print(f'{b[\"name\"][:45]:45s} | Ph:{ph:16s} | Em:{em:20s} | Li:{li:35s} | Own:{ow}')
"

pkill -f "python.*app.py" 2>/dev/null
