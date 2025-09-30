#!/usr/bin/env python3

import concurrent.futures
import socket
import timeit
import argparse

REGIONS = [  # https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
    {"region": "Australia East", "area": "Sydney", "code": "ap-sydney-1"},
    {"region": "Australia Southeast", "area": "Melbourne", "code": "ap-melbourne-1"},
    {"region": "Brazil East", "area": "Sao Paulo", "code": "sa-saopaulo-1"},
    {"region": "Brazil Southeast", "area": "Vinhedo", "code": "sa-vinhedo-1"},
    {"region": "Canada Southeast", "area": "Montreal", "code": "ca-montreal-1"},
    {"region": "Canada Southeast", "area": "Toronto", "code": "ca-toronto-1"},
    {"region": "Chile", "area": "Santiago", "code": "sa-santiago-1"},
    {"region": "France Central", "area": "Paris", "code": "eu-paris-1"},
    {"region": "France South", "area": "Marseille", "code": "eu-marseille-1"},
    {"region": "Germany Central", "area": "Frankfurt", "code": "eu-frankfurt-1"},
    {"region": "India South", "area": "Hyderabad", "code": "ap-hyderabad-1"},
    {"region": "India West", "area": "Mumbai", "code": "ap-mumbai-1"},
    {"region": "Israel Central", "area": "Jerusalem", "code": "il-jerusalem-1"},
    {"region": "Italy Northwest", "area": "Milan", "code": "eu-milan-1"},
    {"region": "Japan Central", "area": "Osaka", "code": "ap-osaka-1"},
    {"region": "Japan East", "area": "Tokyo", "code": "ap-tokyo-1"},
    {"region": "Mexico Central", "area": "Queretaro", "code": "mx-queretaro-1"},
    {"region": "Mexico Northeast", "area": "Monterrey", "code": "mx-monterrey-1"},
    {"region": "Netherlands Northwest", "area": "Amsterdam", "code": "eu-amsterdam-1"},
    {"region": "Saudi Arabia West", "area": "Jeddah", "code": "me-jeddah-1"},
    # {"region": "Serbia Central", "area": "Jovanovac", "code": "eu-jovanovac-1"},
    {"region": "Singapore", "area": "Singapore", "code": "ap-singapore-1"},
    {
        "region": "South Africa Central",
        "area": "Johannesburg",
        "code": "af-johannesburg-1",
    },
    {"region": "South Korea Central", "area": "Seoul", "code": "ap-seoul-1"},
    {"region": "South Korea North", "area": "Chuncheon", "code": "ap-chuncheon-1"},
    {"region": "Spain Central", "area": "Madrid", "code": "eu-madrid-1"},
    {"region": "Sweden Central", "area": "Stockholm", "code": "eu-stockholm-1"},
    {"region": "Switzerland North", "area": "Zurich", "code": "eu-zurich-1"},
    {"region": "UAE Central", "area": "Abu Dhabi", "code": "me-abudhabi-1"},
    {"region": "UAE East", "area": "Dubai", "code": "me-dubai-1"},
    {"region": "UK South", "area": "London", "code": "uk-london-1"},
    {"region": "UK West", "area": "Newport", "code": "uk-cardiff-1"},
    {"region": "US East", "area": "Ashburn", "code": "us-ashburn-1"},
    {"region": "US Midwest", "area": "Chicago", "code": "us-chicago-1"},
    {"region": "US West", "area": "Phoenix", "code": "us-phoenix-1"},
    {"region": "US West", "area": "San Jose", "code": "us-sanjose-1"},
]


class Ping:
    def __init__(self, host, port=443, timeout=10, bind=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.bind = bind

    def _ping_once(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        if self.bind:
            self.sock.bind((self.bind, 0))
        self.sock.connect((self.host, self.port))
        self.sock.close()

    def ping(self):
        return timeit.timeit(self._ping_once, number=1)


def min_avg_max(results):
    min = float("inf")
    max = float("-inf")
    sum = 0
    for res in results:
        if res < min:
            min = res
        if res > max:
            max = res
        sum += res
    avg = sum / len(results)
    return min, avg, max


def ping_check(addr, count=5, timeout=10, bind=None):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(count):
            future = executor.submit(Ping(addr, timeout=timeout, bind=bind).ping)
            futures.append(future)
        for future in futures:
            res = future.result()
            results.append(res * 1000)
    return min_avg_max(results)


class PrettyTable:
    def __init__(self, *args):
        self.table = []
        self.header = args

    def add_row(self, *args):
        self.table.append(args)

    def get_string(self, sortby=None, reversesort=False):
        if sortby:
            self.table.sort(
                key=lambda x: x[self.header.index(sortby)], reverse=reversesort
            )

        max_len = [0] * len(self.header)
        for row in self.table:
            for i, col in enumerate(row):
                if len(str(col)) > max_len[i]:
                    max_len[i] = len(str(col))

        lpadding = 1  # left padding
        rpadding = 2  # right padding
        border = (
            "+"
            + "+".join(
                "-" * (max_len[i] + lpadding + rpadding)
                for i in range(len(self.header))
            )
            + "+\n"
        )
        table = border
        for i, col in enumerate(self.header):
            table += "|" + lpadding * " " + str(col).ljust(max_len[i] + rpadding)
        table += "|\n"
        table += border
        for row in self.table:
            for i, col in enumerate(row):
                table += "|" + lpadding * " " + str(col).ljust(max_len[i] + rpadding)
            table += "|\n"
        table += border
        return table.rstrip("\n")


def main(count, timeout, bind):
    x = PrettyTable("Region", "Area", "Host", "Minimum", "Average", "Maximum")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for ls in REGIONS:
            region = ls.get("region")
            area = ls.get("area")
            addr = f"objectstorage.{ls.get('code')}.oraclecloud.com"
            future = executor.submit(
                ping_check, addr, count=count, timeout=timeout, bind=bind
            )
            futures.append((future, region, area, ls.get("code")))

        for future, region, area, code in futures:
            rtt_min, rtt_avg, rtt_max = future.result()
            x.add_row(
                region,
                area,
                code,
                round(rtt_min, 2),
                round(rtt_avg, 2),
                round(rtt_max, 2),
            )
    print(x.get_string(sortby="Minimum", reversesort=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--count", type=int, default=5, help="Number of pings to send"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=10, help="Timeout in seconds"
    )
    parser.add_argument(
        "-b", "--bind", type=str, default=None, help="Bind to a specific IP address"
    )
    args = parser.parse_args()
    main(args.count, args.timeout, args.bind)
