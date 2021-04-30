import coordinator_stm

#setup of statemachine and mqttClient for Black Box
coordinator_stm.coordinator.client = coordinator_stm.client
coordinator_stm.coordinator.client.stm_driver = coordinator_stm.driver
coordinator_stm.client.start('mqtt.item.ntnu.no', 1883)
coordinator_stm.driver.start()
coordinator_stm.coordinator.stm_driver = coordinator_stm.driver

coordinator_stm.client.is_blackbox = True
coordinator_stm.client.client.subscribe("team2/#", 2)