import paramiko
import re

def copy_member_to_ifs(program_name):

    ifs_path = f"/home/neerjaa/psproject/{program_name}.txt"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
        hostname="www.pub400.com",
        port="2222",
        username="NEERJAA",
        password="neerja123456",
        timeout=30
         )
        print('connection 1 successful')
        #sample comment
        #Main function
        #command = ( "CPYTOIMPF FROMFILE(NEERJAA2/QRPGLESRC {program_name}) TOFILE('/home/neerjaa/psproject/{program_name}.txt') "
        #"MBROPT(*REPLACE) RCDDLM(*CRLF) DTAFMT(*DLM) STRDLM(*NONE) " )
        #command = (
        #    f"system \"CPYTOIMPF "
        #    f"FROMFILE(NEERJAA2/Q  
        #    RPGLESRC {program_name} 
        #    f"TOSTMF('{ifs_path}') "
        #    f"STMFCODPAG(*PCASCII) "
        #    f"RCDDLM(*CRLF) STRDLM(*NONE) "
        #    )
        command = (
            f'system "CPYTOIMPF '
            f'FROMFILE(NEERJAA2/QRPGLESRC {program_name}) '
            f"TOSTMF('{ifs_path}') "
            f'MBROPT(*REPLACE) '
            f'STMFCODPAG(*PCASCII) '
            f'RCDDLM(*CRLF) '
            f'STRDLM(*NONE)"'
            )
        #print("command",command)    
        ssh.exec_command(command)
        ssh.close()
        return ifs_path
    except Exception as e:
        print("Copy Error:", e)
        return None
def Remove_ifsFile(ifs_path):

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
        hostname="www.pub400.com",
        port="2222",
        username="NEERJAA",
        password="neerja123456",
        timeout=30
         )
        command = (
         f'system "RMVLNK '
         f'OBJLNK(\'{ifs_path}\')"'
        )
        #print("command",command)    
        ssh.exec_command(command)
        print(" ")
        print("IFS File removed successfully")   
        ssh.close()
      
    except Exception as e:
        print("Copy Error:", e)
        return None

def generate_pseudocode(program_name):
    indent = 0
    pseudocode = []
    files_declared = []
    Recordformat_updated = set()
    output_files = set()
    operations = set()

    ifs_path = f"/home/neerjaa/psproject/{program_name}.txt"

    def add(text):
        pseudocode.append("    " * indent + text)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
        hostname="www.pub400.com",
        port="2222",
        username="NEERJAA",
        password="neerja123456",
        timeout=30
       )

        #Read directly from IFS
        stdin, stdout, stderr = ssh.exec_command(f"cat {ifs_path}")
        source_code = stdout.read().decode()

        ssh.close()

    except Exception as e:
        return f"Error reading IFS file: {e}"

    lines = source_code.splitlines()

    for raw in lines:
        line = raw.strip()
        upper = line.upper()

        if not line:
            continue

        # ==========================
        # FILE SPEC
        # ==========================
        if upper.startswith("F"):
            file_name = line[1:10].strip()
            attributes = []

            if "U" in upper:
                attributes.append("Update")
            if "A" in upper:
                attributes.append("Add")
            if "K" in upper:
                attributes.append("Keyed")

            if "PRINTER" not in upper:
                files_declared.append(f"{file_name} ({', '.join(attributes)})")
            else:
                output_files.add(file_name)
            
        # ==========================
        # IF
        # ==========================
        elif upper.startswith("IF"):
            condition = re.sub(r"IF\s+", "", line, flags=re.IGNORECASE).replace(";", "")
            add(f"IF {condition} THEN")
            indent += 1            

        elif upper.startswith("ELSE"):
            indent -= 1
            add("ELSE")
            indent += 1

        elif upper.startswith("ENDIF"):
            indent -= 1
            add("END IF")

        # --- READ ---
        if line.upper().startswith("READ THE FILE"):
            file_name = line.split()[1].replace(";", "")
            add("    " * indent + f"Read {file_name}")
            continue

        # --- DOW LOOP ---
        if line.upper().startswith("DOW"):
            condition = line[4:].replace(";", "")
            add("    " * indent + f"Do While {condition}")
            indent += 1
            continue

        # --- ENDDO ---
        if line.upper().startswith("ENDDO"):
            indent -= 1
            add("    " * indent + "End While")
            continue
        # ==========================
        # CHAIN
        # ==========================
        elif upper.startswith("CHAIN"):
            parts = line.replace(";", "").split()
            key = parts[1]
            file = parts[2]
            add(f"Retrieve record from {file} using key {key}")

        # ==========================
        # %FOUND
        # ==========================
        elif "%FOUND" in upper:
            add("IF record is found THEN")
            indent += 1

        # ==========================
        # DELETE
        # ==========================
        elif upper.startswith("DELETE"):
            record = line.split()[1].replace(";", "")
            add(f"Delete record {record}")
            operations.add("DELETE")
            Recordformat_updated.add(record)

        # ==========================
        # WRITE
        # ==========================
        elif upper.startswith("WRITE"):
            record = line.split()[1].replace(";", "")
            add(f"Write record {record}")
            operations.add("WRITE")
            Recordformat_updated.add(record)

        # ==========================
        # LR Indicator
        # ==========================
        elif "*INLR" in upper:
            add("           ")
            add("Program End")
            add("-----------")
            add("Set Last Record indicator ON")

        elif line.lower().startswith("return"):
            add("Return Program Control")
    # ==========================
    # SUMMARY
    # ==========================

    summary = [
        "PROGRAM SUMMARY",
        "---------------",
        f"Program Name         : {program_name}",
        f"Files Declared       : {', '.join(files_declared) if files_declared else 'None'}",
        f"Main Operations      : {', '.join(sorted(operations)) if operations else 'None'}",
        f"Record fmts updated  : {', '.join(Recordformat_updated) if Recordformat_updated else 'None'}",
        f"Print Files created  : {', '.join(output_files) if output_files else 'None'}",
        "",
        "PSEUDOCODE",
        "----------"
    ]

    return "\n".join(summary + pseudocode)

# ==========================
# MAIN FUNCTION
# ==========================
def main():

    program_name = input("Enter RPG Program Name: ").strip().upper()

    print("Copying member to IFS...")
    ifs_path = copy_member_to_ifs(program_name)

    if not ifs_path:
        print("Failed to copy source.")
        return

    print("Generating pseudocode...\n")

    result = generate_pseudocode(program_name)

    print(result)
    Remove_ifsFile(ifs_path)

main()