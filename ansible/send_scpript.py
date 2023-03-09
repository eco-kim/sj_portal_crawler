import os

script_dir = '/Users/ecokim/Desktop/work/research_portal_crawler/crawl/'
pem = '/Users/ecokim/Desktop/aws/master.pem'
ips = {1: '3.34.142.86',
2: '43.201.55.165',
3: '3.38.97.91',
4: '3.34.131.60',
5: '54.180.126.134',
6: '52.78.53.221',
7: '54.180.135.174',
8: '13.125.197.208',
9: '13.125.233.120',
10: '13.125.218.222'}

fname = 'alfa_options.py'
for i in range(1,11):
    with open(script_dir+fname,'r') as f:
        lines= f.readlines()
    lines[22] = f"target = {i}\n"

    with open(script_dir+fname,'w') as f:
        for l in lines:
            f.write(l)    

    os.system(f"scp -i {pem} {script_dir}{fname} ec2-user@{ips[i]}:/home/ec2-user/crawl")