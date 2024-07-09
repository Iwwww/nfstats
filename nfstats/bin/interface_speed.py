import sys
import os
from pathlib import Path
import django
import subprocess
import re
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from mainapp.models import Settings, Host, Interface, Speed
from mainapp.utils import update_globals
import logging

# Set up Django environment
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ["DJANGO_SETTINGS_MODULE"] = "nfstats.settings"
django.setup()

# Initialize logger
logger = logging.getLogger("django")


def clean_dir(dir_name, oldtime_threshold):
    for file_name in Path(dir_name).glob("**/*"):
        if file_name.is_file() and file_name.stat().st_mtime < oldtime_threshold:
            file_name.unlink()
        if file_name.is_dir():
            try:
                next(file_name.iterdir())
            except StopIteration:
                file_name.rmdir()


def main():
    cur_time = int(time.time())
    oldtime_threshold = timezone.now() - timedelta(
        days=int(settings.SYS_SETTINGS["history_days"])
    )
    clean_dir(settings.VARS["data_dir"], oldtime_threshold.timestamp())
    Speed.objects.filter(date__lte=oldtime_threshold).delete()
    hosts = Host.objects.all()
    for host in hosts:
        clean_dir(host.flow_path, oldtime_threshold.timestamp())
        interfaces = Interface.objects.filter(host=host, sampling=True).all()
        for interface in interfaces:
            snmp_err = 0
            OCTETS_OLD_FILE = Path(settings.VARS["data_dir"]).joinpath(
                host.host + "_" + str(interface.snmpid) + ".old"
            )
            command = f"{settings.VARS['snmp_get']} -v{settings.SYS_SETTINGS['snmp_ver']} -Oseq -c {host.snmp_com} {host.host} .1.3.6.1.2.1.31.1.1.1.6.{interface.snmpid}"
            result = subprocess.run(
                [command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            if result.stderr:
                logger.error(
                    f"Host: {host}; Interface: {interface}; Return: {result.stderr.decode('utf-8')} Command: '{command}'"
                )
                snmp_err = 1
            else:
                in_octets = re.search(r".* (\d+)", result.stdout.decode("utf-8")).group(
                    1
                )
            command = f"{settings.VARS['snmp_get']} -v{settings.SYS_SETTINGS['snmp_ver']} -Oseq -c {host.snmp_com} {host.host} .1.3.6.1.2.1.31.1.1.1.10.{interface.snmpid}"
            result = subprocess.run(
                [command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            if result.stderr:
                logger.error(
                    f"Host: {host}; Interface: {interface}; Return: {result.stderr.decode('utf-8')} Command: '{command}'"
                )
                snmp_err = 1
            else:
                out_octets = re.search(
                    r".* (\d+)", result.stdout.decode("utf-8")
                ).group(1)
            if snmp_err == 1:
                if OCTETS_OLD_FILE.exists():
                    OCTETS_OLD_FILE.unlink()
                    logger.error(f"Host: {host}; Interface: {interface}; SNMP Error")
                obj = Speed(
                    in_bps=0,
                    out_bps=0,
                    date=timezone.make_aware(
                        datetime.fromtimestamp(cur_time).replace(second=0)
                    ),
                    interface=interface,
                )
                obj.save()
            else:
                if not OCTETS_OLD_FILE.exists():
                    obj = Speed(
                        in_bps=0,
                        out_bps=0,
                        date=timezone.make_aware(
                            datetime.fromtimestamp(cur_time).replace(second=0)
                        ),
                        interface=interface,
                    )
                    obj.save()
                    try:
                        with open(str(OCTETS_OLD_FILE), "w") as file:
                            file.write(f"{cur_time}:{in_octets}:{out_octets}")
                            logger.info(
                                f"Host: {host}; Interface: {interface}; Created Octets File"
                            )
                            logger.info(
                                f"Host: {host}; Interface: {interface}; Rec to Octets File"
                            )
                    except Exception as e:
                        logger.error(f"(File R/W): {e}")
                        raise
                else:
                    try:
                        with open(str(OCTETS_OLD_FILE), "r") as file:
                            speed_data = file.read().split(":")
                    except Exception as e:
                        logger.error(f"(File R/W): {e}")
                        raise
                    if len(speed_data) == 3:
                        old_time, old_in_octets, old_out_octets = speed_data
                        if (
                            int(in_octets) >= int(old_in_octets)
                            and int(out_octets) >= int(old_out_octets)
                            and int(cur_time) - int(old_time) < 1000
                        ):
                            in_bps = round(
                                (int(in_octets) - int(old_in_octets))
                                * 8
                                / (int(cur_time) - int(old_time)),
                                0,
                            )
                            out_bps = round(
                                (int(out_octets) - int(old_out_octets))
                                * 8
                                / (int(cur_time) - int(old_time)),
                                0,
                            )
                            obj = Speed(
                                in_bps=in_bps,
                                out_bps=out_bps,
                                date=timezone.make_aware(
                                    datetime.fromtimestamp(cur_time).replace(second=0)
                                ),
                                interface=interface,
                            )
                            obj.save()
                            logger.info(
                                f"Host: {host}; Interface: {interface}; Rec to DB"
                            )
                    try:
                        with open(str(OCTETS_OLD_FILE), "w") as file:
                            file.write(f"{cur_time}:{in_octets}:{out_octets}")
                            logger.info(
                                f"Host: {host}; Interface: {interface}; Rec to Octets File"
                            )
                    except Exception as e:
                        logger.error(f"(File R/W): {e}")
                        raise


if __name__ == "__main__":
    main()

