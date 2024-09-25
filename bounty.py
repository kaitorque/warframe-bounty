import re
import json
import os
import time

# ANSI escape codes for colors
COLOR_CODES = {
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "RESET": "\033[0m"
}

# Job stage colors and descriptions mapping
job_data = {
    "Solaris": {
        "colors": {
            "DynamicAssassinate": COLOR_CODES["GREEN"],
            "DynamicCachesAirDrop": COLOR_CODES["GREEN"],
            "DynamicExterminate": COLOR_CODES["GREEN"],
            "DynamicExterminateDrones": COLOR_CODES["GREEN"],
            "DynamicExterminateMoas": COLOR_CODES["GREEN"],
            "DynamicBaseSpy": COLOR_CODES["YELLOW"],
            "DynamicCaches": COLOR_CODES["YELLOW"],
            "DynamicExcavation": COLOR_CODES["YELLOW"],
            "DynamicAmbush": COLOR_CODES["RED"],
            "DynamicDroneDefense": COLOR_CODES["RED"],
            "DynamicRecovery": COLOR_CODES["RED"],
            "DynamicResourceCapture": COLOR_CODES["RED"],
        },
        "descriptions": {
            "DynamicAmbush": "(Defend Coil drive...Time based)",
            "DynamicAssassinate": "(Scale per player)",
            "DynamicBaseSpy": "(Spy inside base...Kinda easy to fail the bonus obj.)",
            "DynamicCaches": "(Find caches inside base...Need to go base)",
            "DynamicCachesAirDrop": "(Find caches...Time based)",
            "DynamicDroneDefense": "(Defend drone while killing...Kinda hard bonus obj.)",
            "DynamicExterminate": f"(Scale per player...Cannot {COLOR_CODES["RED"]}abandoned{COLOR_CODES["GREEN"]})",
            "DynamicExterminateDrones": f"(Scale per player...Cannot {COLOR_CODES["RED"]}abandoned{COLOR_CODES["GREEN"]})",
            "DynamicExterminateMoas": f"(Scale per player...Cannot {COLOR_CODES["RED"]}abandoned{COLOR_CODES["GREEN"]})",
            "DynamicExcavation": "(Standard excavation...Time based, Scale per player)",
            "DynamicRecovery": "(Find Solaris camp...Time based, Cannot abandoned)",
            "DynamicResourceCapture": "(Capture cases...Scale per player, Kinda hard bonus obj.)",
        }
    },
    "Cetus": {
        "colors": {
            "DynamicAssassinate": COLOR_CODES["GREEN"],
            "DynamicCapture": COLOR_CODES["GREEN"],
            "DynamicRescue": COLOR_CODES["GREEN"],
            "HiddenResourceCaches": COLOR_CODES["GREEN"],
            "HiddenResourceCachesCave": COLOR_CODES["YELLOW"],
            "DynamicExterminate": COLOR_CODES["YELLOW"],
            "DynamicHijack": COLOR_CODES["YELLOW"],
            "DynamicSabotage": COLOR_CODES["YELLOW"],
            "DynamicCaveExterminate": COLOR_CODES["RED"],
            "DynamicDefend": COLOR_CODES["RED"],
            "DynamicResourceTheft": COLOR_CODES["RED"],
        },
        "descriptions": {
            "DynamicAssassinate": "(Scale per player)",
            "DynamicCapture": "(Bring Sentinel/Pet that cannot attack)",
            "DynamicCaveExterminate": "(Kill 25 Enemy...Scale per player, Need to go cave)",
            "DynamicDefend": "(Liberation Camp...Time Based)",
            "DynamicExterminate": "(Kill 25 Enemy...Scale per player)",
            "DynamicHijack": f"(Drone...If using {COLOR_CODES["GREEN"]}Volt{COLOR_CODES["YELLOW"]} it is easy)",
            "DynamicRescue": "(Rescue prisoners)",
            "DynamicResourceTheft": "(Armored Vault...Time Based)",
            "DynamicSabotage": "(Complete the bonus obj. before 3rd beacon destroy)",
            "HiddenResourceCaches": "(Open caches)",
            "HiddenResourceCachesCave": "(Open 3 cache...Need to go cave)",
        }
    },
    "Deimos": {
        "colors": {
            "DynamicAssassinate": COLOR_CODES["GREEN"],
            "DynamicCorpusSurvivors": COLOR_CODES["GREEN"],
            "DynamicExcavation": COLOR_CODES["GREEN"],
            "DynamicExcavationEndless": COLOR_CODES["GREEN"],
            "DynamicExterminate": COLOR_CODES["GREEN"],
            "DynamicKeyPieces": COLOR_CODES["GREEN"],
            "DynamicGrineerSurvivors": COLOR_CODES["YELLOW"],
            "DynamicPurify": COLOR_CODES["YELLOW"],
            "DynamicAreaDefense": COLOR_CODES["RED"],
        },
        "descriptions": {
            "DynamicAreaDefense": "(Time Based)",
            "DynamicAssassinate": "(Scale per player)",
            "DynamicCorpusSurvivors": "(Small Time based)",
            "DynamicExterminate": "(Kill 3 Hives)",
            "DynamicExcavation": "(Standard excavation...Time based, Scale per player)",
            "DynamicExcavationEndless": "(Endless excavation)",
            "DynamicGrineerSurvivors": "(Sometimes it is easier to fail the bonus obj.)",
            "DynamicKeyPieces": "(Tumor Cache)",
            "DynamicPurify": "(Scale per player)",
        }
    }
}


def tail_logfile(logfile_path):
    with open(logfile_path, "r", encoding="utf-8", errors='ignore') as file:
        file.seek(0, os.SEEK_END)
        buffer = ""
        while True:
            line = file.readline()
            if line:
                buffer += line
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    job_stages, hub_name = extract_job_stages(line)
                    if job_stages:
                        hub_prefix = get_hub_prefix(hub_name)
                        if hub_prefix:
                            print(f"\nHub name: {hub_name}")
                            display_job_stages(job_stages, hub_prefix)
            else:
                time.sleep(0.1)

def extract_job_stages(line):
    if "Set squad mission:" in line:
        match = re.search(r'\{.*\}', line)
        if match:
            try:
                data = json.loads(match.group(0))
                return data.get("jobStages"), data.get("name")
            except json.JSONDecodeError:
                print("JSON decode error.")
    return None, None

def get_hub_prefix(hub_name):
    if hub_name.startswith("Solaris") or hub_name.startswith("SolNode129"):
        return "Solaris"
    elif hub_name.startswith("Cetus") or hub_name.startswith("SolNode228"):
        return "Cetus"
    elif hub_name.startswith("Deimos") or hub_name.startswith("SolNode229"):
        return "Deimos"
    return None

def display_job_stages(stages, hub_prefix):
    hub_data = job_data.get(hub_prefix)
    if hub_data:
        print("Latest Job Stages:")
        for idx, stage in enumerate(stages, start=1):
            stage_name = stage.split('/')[-1]
            color = hub_data["colors"].get(stage_name, COLOR_CODES["RESET"])
            description = hub_data["descriptions"].get(stage_name, "")
            print(f"{idx}. {color}{stage_name} {description}{COLOR_CODES['RESET']}")

def main(logfile_path):
    print(f"Monitoring log file: {logfile_path}")
    tail_logfile(logfile_path)

if __name__ == "__main__":
    logfile_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Warframe", "EE.log")
    main(logfile_path)
