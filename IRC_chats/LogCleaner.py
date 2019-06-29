import re


def parsed_line(line):
    day_date_regex = re.compile("\[[A-Za-z ]+[a-zA-Z0-9 ]+\] ")
    time_regex = re.compile("\[[0-9: ]+ (?:PM|AM) IST\] ")
    command_regex = re.compile("[a-zA-Z0-9\<\>]+|$")
    
    day_date = re.findall(day_date_regex, line)[0]
    line = re.sub(day_date_regex, '', line)
    time_ = re.findall(time_regex, line)[0]
    line = re.sub(time_regex, '', line)
    command = re.findall(command_regex, line)[0]  

    line = re.sub(command_regex, '', line, 1)
    line = line.strip()
    
    components = {
        "time_": time_,
        "command": command,
        "body": line
    }
    return components


def get_duration(content):
    time_regex = re.compile("\[[0-9: ]+ (?:PM|AM) IST\] ")
    start_time = re.findall(time_regex, content[0])[0]
    end_time = re.findall(time_regex, content[-1])[0]
    
    return (start_time, end_time)


def get_date(content):
    day_date_regex = re.compile("\[[A-Za-z ]+[a-zA-Z0-9 ]+\] ")
    day_date = re.findall(day_date_regex, content[0])[0]
    
    return day_date


participants = set()


def get_clean_line(line):
    global participants
    components = parsed_line(line)
    
    if components["command"] == "Whois":
        line = ''
    if components["command"].startswith("<"):
        participants.add(components['command'].strip("<>"))
        
    line = components["time_"] + components["command"] + "\t" + components["body"] + "\n"
    print(line)
    return line


with open('june_28_eval1_.txt') as f:
    content = f.readlines()
    new_content = list()

timing = get_duration(content)  
date = get_date(content)

for line in content:
    new_content.append(get_clean_line(line))
    

    
with open('june_28_eval1.txt', "w") as f:
    f.write("Date: " + date[1:-2] + "\n")
    f.write("Participants: " + ", ".join(list(participants)) + "\n")
    f.write("Start_Time: " + timing[0][1:-2] + "\n")    
    f.write("End_Time: " + timing[1][1:-2] + "\n")   
    f.write("------------------------------------------------------------------------------\n\n")
    for line in new_content:
        f.write("%s" % line)
        


# In[10]:


participants


# In[ ]:




