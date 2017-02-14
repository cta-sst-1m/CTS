FSM_TABLE = {
            'initial': 'unallocated',
            'events': [
                {'name': 'allocate', 'src': 'unallocated', 'dst': 'not_ready'},
                {'name': 'configure', 'src': 'not_ready', 'dst': 'ready'},
                {'name': 'start_run',  'src': 'ready',    'dst': 'stand_by'},
                {'name': 'start_trigger', 'src': 'stand_by', 'dst': 'running'},
                {'name': 'stop_trigger', 'src': 'running', 'dst': 'stand_by'},
                {'name': 'stop_run', 'src': 'stand_by', 'dst': 'ready'},
                {'name': 'reset', 'src': 'ready', 'dst': 'not_ready'},
                {'name': 'deallocate', 'src': 'not_ready', 'dst': 'unallocated'},
                {'name': 'abort', 'src': ['ready', 'stand_by', 'running'], 'dst': 'not_ready'}
            ]
        }