# for file in c_target_files:
#     passes = False
#     log(f"\nChecking file {file.repository.name}/{file.name}... ", end="")
#     #passes = False #break out of loop if file passes
#     try:
#         content = file.decoded_content.decode()
#     except:
#         log("Failure to read file!")
#         continue
#     
#     for header in c_libraries_to_check:
#         if content.find(header)>0:
#             log(f"Found {header}!", end="")
#             passing_files.append(file)
#             passes = True
#             break
#         
#     if passes: continue
#     
#     for local_header in c_passing_headers:
#         if local_header.repository.name != file.repository.name: continue
#         header = local_header.name
#         if content.find(header)>0:
#             log(f"Found {header}!", end="")
#             passing_files.append(file)
#             break
# #     """  
# #     length = len(content)
# #     for i in range(length//min_length): #iterate every x characters
# #         if passes: break
# #         c = content[i*min_length]
# #         for header in libraries_to_check:
# #             index = header.find(c)
# #             if index<0: break #wrong character
# #             
# #             start = (i*min_length)-index
# #             if content[start:start+len(header)] == header or content[start-1:start+len(header)-1] == header:
# #                 print(f"Found {header}!", end="")
# #                 passing_files.append(file)
# #                 passes = True
# #                 break
# #             
# #         for local_header in passing_headers:
# #             if local_header.repository != file.repository: continue
# #             header = local_header.name #Reassigning name because I'm lazy
# #             
# #             #Figure out if c is in header and if header is in file
# #             index = header.find(c)
# #             if index<0: break #wrong character
# #             header_found = False
# #             
# #             for j in range(len(header)):
# #                 if header[j] == c:
# #                     start = (i*min_length) - j
# #                     header_found = content[start:start+len(header)] == header
# #                 if header_found: break
# #                     
# #             if header_found:
# #                 print(f"Found {header}!", end="")
# #                 passing_files.append(file)
# #                 passes = True
# #                 break
# #     """
# 
# for file in f_target_files:
#     passes = False
#     log(f"\nChecking file {file.repository.name}/{file.name}... ", end="")
#     #passes = False #break out of loop if file passes
#     try:
#         content = file.decoded_content.decode()
#     except:
#         log("Failure to read file!")
#         continue
#     
#     for header in f_libraries_to_check:
#         if content.find(header)>0:
#             log(f"Found {header}!", end="")
#             passing_files.append(file)
#             passes = True
#             break
#         
#     if passes: continue
#     
#     for local_header in f_passing_headers:
#         if local_header.repository.name != file.repository.name: continue
#         header = local_header.name
#         if content.find(header)>0:
#             log(f"Found {header}!", end="")
#             passing_files.append(file)
#             break


def search_for_text(files, text):
    passing_files = []
    min_length = min([len(s) for s in text])
    for file in files:
        passes = False #break out of loop if file passes
        try:
            content = file.decoded_content.decode()
        except:
            continue
            
        length = len(content)
        for i in range(length//min_length): #iterate every x characters
            if passes: break
            c = content[i*min_length]
            for val in text:
                index = val.find(c)
                if index<0: break #wrong character
                
                start = (i*min_length)-index
                if content[start:start+len(val)] == val or content[start-1:start+len(val)-1] == val:
                    log(f"Found {val} in file {file.name}!")
                    passing_files.append(file)
                    passes = True
                    break
                
    return passing_files