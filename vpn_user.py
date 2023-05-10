import json
# 读取文件并转换为字
with open('./resources/psw-file', 'r') as f:
	content = f.readlines()
new_content = []
for line in content:
	if line.strip():
		new_content.append(line)

result= []

for line in new_content:
	fields = line.strip().split()
	data = {
		"displayName": fields[0],
		"pass": fields[1],
		"cn_name": fields[2]
	}
	result.append(data)
json_result = json.dumps(result)

def vpn_pass(name):
	for item in result:
		if item["displayName"] == name:
			vpn_pass = item["pass"]
			return item
			break
	else:
		return False
