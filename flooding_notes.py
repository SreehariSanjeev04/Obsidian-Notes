from pathlib import Path

content = r"""# Flooding Attack — DoS / DDoS Notes

## 1. What is a DoS attack?

**Denial of Service (DoS)** is an attack whose goal is to make a network, host, or service unavailable or significantly degraded for legitimate users.

The core idea is **resource exhaustion**:

\[
\text{Attacker-induced demand} > \text{Available capacity}
\]

The exhausted resource may be:

- Network bandwidth
- Router/interface packet-processing capacity
- Queue/buffer space
- TCP connection state
- CPU
- Memory
- Application workers
- Database connections or other application resources

A DoS does **not** necessarily mean that the attacker simply sends a huge amount of traffic.

---

## 2. DoS vs DDoS

### DoS

A single source (or a small number of sources) attempts to exhaust a target's resources.

```text
Attacker
   |
   | traffic
   v
Victim
DDoS

A Distributed Denial of Service (DDoS) attack uses many distributed systems/sources to generate traffic or requests toward the victim.

                 +---- Source 1 ---\
                 +---- Source 2 ----\
                 +---- Source 3 -----\
                 +---- Source 4 ------> Victim
                 +---- Source 5 -----/
                 +---- Source 6 ----/

The advantage to the attacker is aggregate capacity and the difficulty of blocking all sources individually.

Kurose & Ross discusses this distributed model using compromised machines ("zombies") and illustrates DDoS in Figure 1.25.

3. Kurose & Ross classification of DoS attacks

Kurose & Ross, Computer Networking: A Top-Down Approach, 8th ed., Chapter 1, §1.6 "Networks Under Attack", describes three broad categories:

3.1 Vulnerability attacks

A relatively small number of specially constructed packets/messages exploit a vulnerability and cause the target system to crash or stop functioning.

The important point:

High traffic volume is not required.

3.2 Bandwidth flooding

The attacker sends enough traffic to consume the victim's access-link capacity.

Example:

Legitimate traffic: 300 Mb/s
Attack traffic:     1.5 Gb/s
Victim link:        1 Gb/s

The link becomes the bottleneck.

Consequences:

queue grows
   ↓
delay increases
   ↓
buffer fills
   ↓
packets are dropped
   ↓
legitimate traffic is affected

The target resource is primarily:

$$ \boxed{\text{Network bandwidth}} $$
3.3 Connection flooding

The attacker attempts to consume the target's connection-handling resources by creating huge numbers of TCP connections, including large numbers of incomplete/half-open connections.

Possible exhausted resources:

TCP connection state
Connection backlog
Memory
CPU
Socket resources

A classic example is a TCP SYN flood.

4. Why flooding works: networking foundation

A network is made of components with finite capacity.

Internet
   |
   v
[Access Link]
   |
   v
[Router / NIC]
   |
   v
[Kernel]
   |
   v
[TCP / UDP]
   |
   v
[Application]
   |
   v
[Database]

Every stage has a finite processing capacity.

A flooding attack succeeds when traffic/work arrives faster than the relevant resource can handle it.

General model:

$$ \boxed{\lambda > \mu} $$

where:

\(\lambda\) = arrival/work rate
\(\mu\) = service/processing rate

When this persists:

queues grow
delay increases
buffers fill
packets/requests are dropped
legitimate users experience degradation or denial of service

This connects flooding directly to Kurose & Ross Chapter 1 §1.4, which covers delay, queuing, packet loss, and throughput.

5. Bandwidth flooding

The attacker attempts to saturate the victim's network path.

                    Legitimate traffic
                           |
                           v
                     +-----------+
                     | Internet  |
                     +-----------+
                           |
                           | 1 Gb/s link
                           v
                     +-----------+
                     |  Victim   |
                     +-----------+
                           ^
                           |
                    huge traffic
                           |
                    +------+------+
                    | DDoS sources|
                    +-------------+

Suppose:

$$ C = 1\text{ Gb/s} $$

is the victim's access link.

If incoming traffic is:

$$ T = 2\text{ Gb/s} $$

then the link cannot carry all of the traffic.

The excess traffic must be:

queued, or
dropped.

Eventually the service becomes effectively unavailable.

Key resource
$$ \boxed{\text{Link capacity}} $$
Typical measurements
bits/sec
packets/sec
interface utilization
packet drop rate
6. Packet rate vs bandwidth

A flood does not have to be judged only by bits/sec.

Two traffic streams can have the same bandwidth but very different packet rates.

For example:

Traffic A:
large packets
low packets/sec

Traffic B:
small packets
very high packets/sec

Traffic B may put much more pressure on:

packet-processing CPU
interrupt handling
router/NIC processing
firewall rule evaluation

So a network engineer should monitor both:

$$ \boxed{\text{bits/sec}} $$

and

$$ \boxed{\text{packets/sec}} $$
7. TCP SYN flood
Normal TCP three-way handshake

A normal TCP connection starts as:

Client                         Server

   | -------- SYN ------------> |
   |                            |
   | <------ SYN + ACK -------- |
   |                            |
   | -------- ACK ------------> |
   |                            |
   |     connection established |

Important TCP concepts:

SYN
SYN-ACK
ACK
Sequence numbers
Connection state

Primary source: Kurose & Ross, 8th ed., Chapter 3, §3.5.1 and §3.5.6.

What happens in a SYN flood?

The attacker sends many SYN requests without completing the normal handshake.

Attacker                         Victim

   | -------- SYN ------------> |
   | -------- SYN ------------> |
   | -------- SYN ------------> |
   | -------- SYN ------------> |
   | -------- SYN ------------> |
   |             ...            |

The victim must keep state for connection attempts that are not completing.

Conceptually:

                 incoming SYNs
                      |
                      v
               +--------------+
               | TCP listener |
               |   backlog    |
               |              |
               | [SYN] [SYN]  |
               | [SYN] [SYN]  |
               | [SYN] [SYN]  |
               +--------------+
                      |
                  fills up
                      |
                      v
            legitimate attempts
              are affected

The attack therefore targets connection/state resources, not necessarily just bandwidth.

Core relationship
$$ \text{SYN arrival rate} > \text{connection completion/cleanup rate} $$

for a sufficient period can cause resource exhaustion.

8. Why SYN floods are different from bandwidth floods
Bandwidth flood

Attacker primarily consumes:

$$ \boxed{\text{bits/sec or packets/sec}} $$
SYN flood

Attacker primarily attempts to consume:

$$ \boxed{\text{TCP pending connection/state resources}} $$

A SYN flood can therefore cause serious impact even without completely saturating the external link.

9. UDP flooding

UDP is connectionless.

There is no TCP-style three-way handshake.

Therefore an attacker can send UDP datagrams directly toward a target service.

Attacker
   |
   +---- UDP ----\
   +---- UDP -----\
   +---- UDP ------> Target
   +---- UDP -----/
   +---- UDP ----/

Potential bottlenecks include:

bandwidth
packets/sec
CPU
UDP/socket processing
application processing

Primary source: Kurose & Ross, 8th ed., Chapter 3, §3.3.

Nmap's TCP/IP reference also provides UDP header details useful when analyzing UDP flood traffic.

10. ICMP flooding

ICMP can also be used to generate large volumes of traffic.

DDoS sources
   |
   +---- ICMP ----\
   +---- ICMP -----\
   +---- ICMP ------> Victim
   +---- ICMP -----/
   +---- ICMP ----/

A historical DDoS example discussed by Kurose & Ross involved large quantities of ICMP ping messages directed toward DNS root-server infrastructure.

This can consume:

bandwidth
packet-processing capacity
server/router resources

Source: Kurose & Ross, 8th ed., §1.6, discussion of DDoS and ICMP flooding.

11. Smurf attack

A classic historical attack is the Smurf attack, which combines:

IP source-address spoofing
ICMP
broadcast amplification

Conceptual flow:

Attacker
   |
   | ICMP request
   | source IP = victim
   v
Broadcast network
   |
   +------ reply ------\
   +------ reply -------\
   +------ reply -------> Victim
   +------ reply -------/
   +------ reply ------/

The attacker causes many systems to send responses toward the victim.

The important networking idea is:

$$ \text{Traffic generated by attacker} < \text{Traffic delivered to victim} $$

because the intermediary systems amplify the traffic.

Source: Wenliang Du / SEED Labs TCP/IP Attack material, which includes Smurf attacks among the TCP/IP attack exercises.

12. Application/resource exhaustion

Flooding does not have to be purely volumetric.

A service can be attacked by making each request expensive.

Suppose:

Normal request = 10 ms CPU
Expensive request = 500 ms CPU

An attacker who sends expensive requests can consume CPU much faster than ordinary traffic would.

Attacker
   |
   | expensive requests
   v
+--------------------+
| Application server |
|                    |
| CPU → 100%         |
+--------------------+
          |
          v
legitimate requests
become slow/rejected
Forshaw's perspective

James Forshaw, Attacking Network Protocols, Chapter 9 "The Root Causes of Vulnerabilities", explicitly discusses:

Denial-of-Service
Memory Exhaustion Attacks
Storage Exhaustion Attacks
CPU Exhaustion Attacks
Algorithmic Complexity

This broadens the definition:

$$ \boxed{\text{DoS = exhaustion of a critical resource}} $$

not simply:

$$ \text{DoS = high network bandwidth} $$
13. Memory exhaustion

A network interaction may cause the server to allocate memory.

Conceptually:

network request
      ↓
memory allocation
      ↓
many requests
      ↓
memory consumption grows
      ↓
memory exhausted
      ↓
service failure

This may happen with:

oversized inputs
too many simultaneous operations
retained connection state
poorly bounded buffers
protocol implementation bugs

Source: Forshaw, Chapter 9, "Memory Exhaustion Attacks."

14. CPU exhaustion

A protocol or application can require significant computation.

An attacker may exploit this by causing expensive processing repeatedly.

request
   ↓
expensive computation
   ↓
repeat
   ↓
CPU saturation
   ↓
legitimate requests delayed

Forshaw specifically discusses CPU Exhaustion Attacks and Algorithmic Complexity in Chapter 9.

15. Storage exhaustion

Network requests can cause logs or other persistent data to be written.

requests
   ↓
logs
   ↓
logs
   ↓
logs
   ↓
disk fills
   ↓
service/system problems

So network traffic can indirectly cause a storage-based DoS.

Source: Forshaw, Chapter 9, "Storage Exhaustion Attacks."

16. Nmap's role

Nmap is not primarily a DoS textbook.

Its value is in understanding how actual packets behave.

Official Nmap TCP/IP Reference

Provides packet-level references for:

IPv4
TCP
UDP
ICMP
Nmap Chapter 3 — Host Discovery

Relevant concepts:

ICMP probing
TCP SYN probing
TCP ACK probing
UDP probing
ARP scanning
Nmap Chapter 5 — Port Scanning Techniques

Relevant concepts:

SYN behavior
SYN/ACK response
RST response
UDP behavior
TCP flags

These are useful when identifying and analyzing flooding traffic in packet captures.

17. Purdy: Linux firewall perspective

Gregor N. Purdy's Linux iptables Pocket Reference is primarily about:

Netfilter
iptables
packet filtering
connection tracking
accounting
NAT
stateful/stateless firewalls
matches and targets

Conceptual packet-filtering path:

Packet
  ↓
Netfilter
  ↓
Table
  ↓
Chain
  ↓
Rule
  ↓
Match
  ↓
Target
  ↓
ACCEPT / DROP / REJECT / ...

Source: Purdy, Linux iptables Pocket Reference, "Concepts," p. 2 onward; "Connection Tracking," p. 14; NAT material pp. 17–20.

18. Rate limiting

A firewall can sometimes reduce the effect of a flood by limiting the rate of packets/connections accepted by a service.

Conceptually:

incoming traffic
       |
       v
+--------------+
| rate limiter |
+--------------+
       |
       v
    service

Purdy's iptables reference includes the limit match and discusses limiting connection attempts.

This can protect the service, but there is a critical limitation:

A local firewall cannot restore bandwidth that has already been consumed by a saturated upstream access link.

19. Why DDoS is harder to defend against than DoS

Single-source:

Attacker A
   |
   v
Victim

Potential defense:

DROP source A

Distributed:

A \
B  \
C   \
D    ---> Victim
E   /
F  /
G /

Blocking one source does little.

The defender must distinguish:

legitimate distributed traffic
            vs
malicious distributed traffic

That is much harder.

Source: Kurose & Ross, 8th ed., §1.6, discussion of DDoS and its distributed nature.

20. Why defense location matters

Consider:

Internet
   |
   | 10 Gb/s attack
   v
[Victim access link]
   |
   v
[Firewall]
   |
   v
[Server]

Suppose the access link is only:

$$ 1\text{ Gb/s} $$

The firewall may successfully drop most attack packets, but the link itself is already overwhelmed.

Therefore:

Host/local mitigation

Useful for:

TCP state exhaustion
CPU exhaustion
application overload
connection limiting
Upstream mitigation

Necessary when the problem is:

access-link saturation
large volumetric floods

This is one reason DDoS mitigation often happens in upstream network infrastructure rather than solely on the victim host.

21. How to recognize a flood

A network specialist should look at multiple dimensions.

Traffic volume
bits/sec
packets/sec
Packet distribution
source IPs
destination IPs
source ports
destination ports
protocol
TCP behavior

For SYN-related problems:

SYN/sec
SYN-ACK/sec
ACK/sec
RST/sec
number of pending connections
Resource utilization
CPU
memory
socket/connection state
queue depth
packet drops
interface utilization
Application behavior
requests/sec
response latency
error rate
active workers
database connections
22. Flooding attack as a queueing problem

A useful mathematical mental model is:

$$ \lambda = \text{arrival rate} $$ $$ \mu = \text{service rate} $$

If:

$$ \lambda < \mu $$

the system can generally keep up.

If:

$$ \lambda > \mu $$

the queue tends to grow.

If the queue/buffer is finite:

$$ Q_{\max} $$

then eventually:

$$ Q \rightarrow Q_{\max} $$

and packets/requests begin to be discarded or rejected.

This explains why flooding leads to:

high traffic
   ↓
queue growth
   ↓
higher latency
   ↓
packet/request loss
   ↓
service degradation
   ↓
denial of service

Primary networking source: Kurose & Ross, 8th ed., §1.4.

23. Layer-by-layer view of flooding

Think about an end-to-end path:

Application
     ↑
     |
Transport (TCP/UDP)
     ↑
     |
Network (IP)
     ↑
     |
Link (Ethernet/Wi-Fi)
     ↑
     |
Physical/network interface

Different attacks stress different layers/resources.

Attack	Typical layer/resource
ICMP flood	Network layer / bandwidth / packet processing
UDP flood	Transport + network / bandwidth / packet processing
SYN flood	TCP state / connection backlog
TCP connection flood	Connection state / CPU / memory
HTTP/application flood	Application CPU/workers/database
Memory exhaustion	Host memory
Storage exhaustion	Disk/storage
CPU exhaustion	Host CPU
24. DoS is not always DDoS

Remember:

$$ \boxed{\text{DDoS} \subset \text{DoS}} $$

DDoS is a distributed form of denial of service.

All DDoS attacks are DoS attacks, but not all DoS attacks are DDoS.

25. DoS is not always flooding

Also remember:

$$ \boxed{\text{Flooding} \subset \text{DoS techniques}} $$

A vulnerability-based DoS may require very few packets.

For example:

malformed input
      ↓
software vulnerability
      ↓
crash
      ↓
service unavailable

No massive traffic volume is necessary.

26. Key differences to memorize
Concept	Main resource exhausted
Bandwidth flood	Link capacity
Packet-rate flood	Packet-processing capacity
SYN flood	TCP pending connection/state
Connection flood	Sockets/state/CPU/memory
Application flood	CPU/workers/database
Memory exhaustion	RAM
Storage exhaustion	Disk
CPU exhaustion	CPU
Vulnerability DoS	Software availability
27. The specialist mental model

Do not memorize:

"DDoS = many computers sending lots of packets."

Instead memorize:

$$ \boxed{ \text{DDoS = distributed resource exhaustion} } $$

with:

$$ \boxed{ \text{Demand} > \text{Capacity} } $$

for some critical resource.

Then ask four questions:

What is the traffic/request rate?
Which resource is becoming exhausted?
At which layer does that resource exist?
Where can the attack be stopped before that resource is exhausted?

Those four questions are enough to analyze most flooding scenarios.

28. Exact textbook sources
Kurose & Ross

James F. Kurose and Keith W. Ross, Computer Networking: A Top-Down Approach, 8th ed., Pearson, 2020

Most relevant:

Chapter 1, §1.4 — Delay, Loss, and Throughput in Packet-Switched Networks
queueing delay
packet loss
throughput
Chapter 1, §1.6 — Networks Under Attack
vulnerability attacks
bandwidth flooding
connection flooding
DDoS
Chapter 3, §3.3 — Connectionless Transport: UDP
Chapter 3, §3.5.1 — The TCP Connection
Chapter 3, §3.5.6 — TCP Connection Management

Useful 8th-edition page references:

§1.4: approximately pp. 35–43
§1.6: approximately pp. 54–57
DDoS discussion / Figure 1.25: approximately pp. 55–56
Gordon Lyon / Nmap

Gordon Lyon, Nmap Network Scanning: The Official Nmap Project Guide to Network Discovery and Security Scanning, Nmap Project, 2009

Relevant official sections:

TCP/IP Reference
IPv4 header
TCP header
UDP header
ICMP header
Chapter 3 — Host Discovery
TCP SYN/ACK probing
UDP ping
ICMP ping
Chapter 5 — Port Scanning Techniques
SYN scanning
TCP response behavior
UDP scanning

Official source:

https://nmap.org/book/

James Forshaw

James Forshaw, Attacking Network Protocols: A Hacker's Guide to Capture, Analysis, and Exploitation, No Starch Press, 2017

Relevant source:

Chapter 9 — The Root Causes of Vulnerabilities
Denial-of-Service
Memory Exhaustion Attacks
Storage Exhaustion Attacks
CPU Exhaustion Attacks
Algorithmic Complexity

The chapter's discussion is especially useful for understanding DoS as resource exhaustion beyond simple bandwidth flooding.

Gregor N. Purdy

Gregor N. Purdy, Linux iptables Pocket Reference, O'Reilly Media, 2004

Relevant source:

"Concepts" — p. 2 onward
"Connection Tracking" — p. 14
"Accounting" — p. 16
"Network Address Translation" — p. 17
"Source NAT and Masquerading" — p. 18
"Destination NAT" — p. 19
"Stateless and Stateful Firewalls" — p. 20
limit, state, TCP, UDP and ICMP matching material in the command reference
Wenliang Du

Wenliang Du, Computer & Internet Security: A Hands-on Approach, 2nd ed.

Most relevant associated material:

TCP/IP Attack material — SYN Flooding
TCP attacks
Smurf attacks
Packet sniffing/spoofing
Firewall / Netfilter / iptables

The SEED Labs TCP/IP Attack Lab specifically covers SYN flooding and the TCP three-way handshake/resource-exhaustion mechanism.

29. One-page revision sheet
FLOODING DoS / DDoS
====================

Goal:
    Exhaust a finite resource and deny legitimate service.

Core equation:
    Demand > Capacity

DoS:
    One/few sources

DDoS:
    Many distributed sources

Kurose categories:
    1. Vulnerability attack
    2. Bandwidth flooding
    3. Connection flooding

Bandwidth flood:
    consume link capacity
    measure: bits/s, packets/s

Packet-rate flood:
    overwhelm packet processing
    measure: packets/s, CPU

SYN flood:
    many SYNs
       ↓
    incomplete handshakes
       ↓
    TCP pending state/backlog consumed
       ↓
    legitimate connections affected

UDP/ICMP flood:
    high packet/traffic volume
       ↓
    bandwidth / packet-processing exhaustion

Application/resource exhaustion:
    expensive requests
       ↓
    CPU/memory/workers/database exhausted

Important distinction:
    Not every DoS is a flood.
    Not every flood is DDoS.

Defense:
    Host-level:
       rate limits
       state controls
       connection controls
       resource limits

    Upstream:
       filtering/scrubbing
       needed when access link is saturated

Key diagnostic questions:
    1. What is arriving?
    2. At what rate?
    3. Which resource is exhausted?
    4. At what network layer?
    5. Where can traffic be filtered?
Reference links
Kurose & Ross, 8th-edition supporting material: https://www-net.cs.umass.edu/kurose_ross/

Nmap official book: https://nmap.org/book/

Nmap TCP/IP reference: https://nmap.org/book/tcpip-ref.html

Forshaw, Attacking Network Protocols: https://nostarch.com/networkprotocols

O'Reilly, Linux iptables Pocket Reference: https://www.oreilly.com/library/view/linux-iptables-pocket/9780596801861/

SEED Labs TCP/IP Attack Lab: https://seedsecuritylabs.org/

"""
path = Path("/mnt/data/flooding_attack_notes.md")
path.write_text(content, encoding="utf-8")
print(path)
