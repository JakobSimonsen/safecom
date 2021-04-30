import coordinator_stm
coordinator_stm.client.is_blackbox = True
coordinator_stm.client.client.subscribe("team2/#", 2)