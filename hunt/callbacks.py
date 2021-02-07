import spoilr.signals_register as signals

signals.register(signals.metapuzzle_answer_correct_message,
                 'hunt.actions.puzzle_solved')

signals.register(signals.puzzle_answer_correct_message,
                 'hunt.actions.puzzle_solved')

signals.register(signals.start_team_message,
                 'hunt.actions.start_team')

signals.register(signals.start_all_message,
                 'hunt.actions.start_all')

signals.register(signals.interaction_accomplished_message,
                 'hunt.actions.interaction_finished')

signals.register(signals.interaction_released_message,
                 'hunt.actions.interaction_released')

signals.register(signals.puzzle_released_message, 'hunt.actions.puzzle_released')
signals.register(signals.puzzle_found_message, 'hunt.actions.puzzle_found')

signals.register(signals.round_released_message, 'hunt.actions.round_released')

signals.register(signals.juice_update_message, 'hunt.mmo_unlock.juice_update_wrapper')

signals.register(signals.puzzle_answer_correct_message, 'hunt.mmo_unlock.puzzle_update')
signals.register(signals.metapuzzle_answer_correct_message, 'hunt.mmo_unlock.puzzle_update')
signals.register(signals.puzzle_found_message, 'hunt.mmo_unlock.puzzle_update')
signals.register(signals.puzzle_released_message, 'hunt.mmo_unlock.puzzle_update')
signals.register(signals.puzzle_deleted_message, 'hunt.mmo_unlock.puzzle_update')

signals.register(signals.interaction_accomplished_message, 'hunt.mmo_unlock.interaction_update')
signals.register(signals.interaction_released_message, 'hunt.mmo_unlock.interaction_update')

signals.register(signals.round_released_message, 'hunt.mmo_unlock.round_update')

signals.register(signals.get_state_message, 'hunt.mmo_unlock.get_state')

signals.register(signals.team_log_message, 'hunt.notifications.notify_team_log')
signals.register(signals.hq_update_message, 'hunt.notifications.notify_hq_update')
