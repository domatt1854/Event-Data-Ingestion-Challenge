#!/usr/bin/env python3

"""
This python module contains values that are used by lookup_agenda.py, test_lookup_agenda.py, and import_agenda.py
"""

# table column names
SESSIONS_COLS = ('session_id', 'parent_session_id','title', 'location', 'description', 'session_type')
SESSIONS_SPEAKERS_COLS = ('session_id', 'speaker_id')
SPEAKERS_COLS = ('speaker_id', 'speaker_name')

# table names
SESSIONS_TABLE_NAME = "sessions"
SESSIONS_SPEAKERS_TABLE_NAME = "sessions_speakers"
SPEAKERS_TABLE_NAME = "speakers"

# valid lookup columns for lookup_agenda.py
LOOKUP_COLS = ('date', 'time_start', 'time_end', 'title', 'location', 'description', 'speaker')


# descriptions to test for test_lookup_agenda.py
test_descriptions = [
            """Cloud operating systems provide on-demand, scalable compute and storage resources. They allow service developers to focus on their business logic by simplifying many portions of their service, including resource management, provisioning, monitoring, and application lifecycle management. This talk describes some of the technical challenges faced, as well as emergent opportunities created, by Microsoft's cloud operating system Windows Azure.""",

            """This is the Approximate Computing session.""",

            """Paravirtualization is an important I/O virtualization technology since it uniquely provides all of the following benefits: the ability to share the device between multiple VMs, support for legacy devices without virtualization hardware, and high performance. However, existing paravirtualization solutions have one main limitation: they only support one I/O device class, and would require significant engineering effort to support new device classes and features.""",

            """In the last decade, the availability of massive amounts of new data, and the development of new machine learning technologies, have augmented reasoning systems to give rise to a new class of computing systems. These Cognitive Systems learn from data, reason from models, and interact naturally with us, to perform complex tasks better than either humans or machines can do by themselves. In essence, cognitive systems help us perform like the best in each domain by penetrating the complexity of big data and leveraging the power of models. O ne of the first cognitive systems, Watson, demonstrated through a Jeopardy! exhibition match, that it was capable of answering complex factoid questions as effectively as the worlds champions. Follow-on cognitive systems perform other tasks, such as discovery, reasoning, and multi-modal understanding in a variety of domains, such as healthcare, insurance, and education. We believe such cognitive systems will transform every profession, industry, and our everyday life for the better. In this talk, I will give an overview of the applications and key capabilities of cognitive systems, and highlight the role pervasive computing will play in such systems.""",
           """Commodity heterogeneous systems (e.g., integrated CPUs and GPUs), now support a unified, shared memory address space for all components. Because the latency of global communication in a heterogeneous system can be prohibi-tively high, heterogeneous systems (unlike homogeneous CPU systems) provide synchronization mechanisms that only guarantee ordering among a subset of threads, which we call a scope. Unfortunately, the consequences and se-mantics of these scoped operations are not yet well under-stood. Without a formal and approachable model to reason about the behavior of these operations, we risk an array of portability and performance issues.

In this paper, we embrace scoped synchronization with a new class of memory consistency models that add scoped synchronization to data-race-free models like those of C++ and Java. Called sequential consistency for heterogeneous-race-free (SC for HRF), the new models guarantee SC for programs with "sufficient" synchronization (no data races) of "sufficient" scope. We discuss two such models. The first, HRF-direct, works well for programs with highly regular parallelism. The second, HRF-indirect, builds on HRF-direct by allowing synchronization using different scopes in some cases involving transitive communication. We quanti-tatively show that HRF-indirect encourages forward-looking programs with irregular parallelism by showing up to a 10% performance increase in a task runtime for GPUs."""
]