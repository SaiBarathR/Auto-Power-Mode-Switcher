import subprocess
import re
from tkinter import Tk, Text, Button, END

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if command[1]!= '/LIST':
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.returncode!= 0:
                print(f"Command failed with return code: {result.returncode}")
            if result.stdout:
                print(f"Output: {result.stdout}")        
        return result
    except Exception as e:
        print(f"An error occurred while running command: {command}")
        print(str(e))
        return None

def get_current_power_plan():
    result = run_command(['powercfg', '/GETACTIVESCHEME'])
    if result and result.returncode == 0:
        match = re.search(r'Power Scheme GUID: ([\w-]+)\s+\((.+)\)', result.stdout)
        if match:
            return match.group(1), match.group(2)
    return None, None

def get_all_power_plans():
    result = run_command(['powercfg', '/LIST'])
    if result and result.returncode == 0:
        plans = re.findall(r'Power Scheme GUID: ([\w-]+)\s+\((.+)\)', result.stdout)
        return plans
    return []

def set_power_plan(plan_guid):
    result = run_command(['powercfg', '/SETACTIVE', plan_guid])
    return result and result.returncode == 0

def display_window(message):
    def close_window():
        root.destroy()

    root = Tk()
    root.title("Power Plan Switcher")
    root.geometry("400x200")

    text_area = Text(root)
    text_area.pack(pady=10)
    text_area.insert(END, message)

    ok_button = Button(root, text="OK", command=close_window)
    ok_button.pack(pady=1)

    root.mainloop()

def main():
    messages = []
    current_guid, current_name = get_current_power_plan()
    if current_guid and current_name:
        messages.append(f"Currently selected power plan: {current_name} (GUID: {current_guid})" + "\n")
    else:
        messages.append("Unable to determine the current power plan.")

    plans = get_all_power_plans()
    game_turbo_guid = None
    high_perf_guid = None

    for guid, name in plans:
        if "gameturbo (high performance)" in name.lower():
            game_turbo_guid = guid
        elif "high performance" in name.lower():
            high_perf_guid = guid

    if game_turbo_guid and high_perf_guid:
        if "gameturbo (high performance)" in current_name.lower():
            messages.append("Switching to High Performance plan.")
            set_power_plan(high_perf_guid)
        else:
            messages.append("Switching to GameTurbo (High Performance) plan.")
            set_power_plan(game_turbo_guid)
    else:
        messages.append("Neither GameTurbo (High Performance) nor High Performance plan found.")

    display_message = "\n".join(messages)
    display_window(display_message)

if __name__ == "__main__":
    main()