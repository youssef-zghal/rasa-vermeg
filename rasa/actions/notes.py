# allowempty: True
# mapping:
#   version:
#     type: "str"
#     required: False
#     allowempty: False
#   intents:
#     type: "seq"
#     sequence:
#     - type: "map"
#       mapping:
#         use_entities:
#           type: "any"
#         ignore_entities:
#           type: "any"
#       allowempty: True
#     - type: "str"
#   entities:
#     type: "seq"
#     matching: "any"
#     sequence:
#       - type: "map"
#         mapping:
#           roles:
#             type: "seq"
#             sequence:
#               - type: "str"
#           groups:
#             type: "seq"
#             sequence:
#             - type: "str"
#         allowempty: True
#       - type: "str"
#   actions:
#     type: seq
#     matching: "any"
#     seq:
#       - type: str
#       - type: map
#         mapping:
#           regex;([A-Za-z]+):
#             type: map
#             mapping:
#               send_domain:
#                 type: "bool"
#   responses:
#     # see shared/nlu/training_data/schemas/responses.yml
#     include: responses

#   slots:
#     type: "map"
#     allowempty: True
#     mapping:
#       regex;([A-Za-z]+):
#         type: "map"
#         allowempty: True
#         mapping:
#           influence_conversation:
#             type: "bool"
#             required: False
#           type:
#             type: "any"
#             required: True
#           values:
#             type: "seq"
#             sequence:
#               - type: "any"
#             required: False
#           min_value:
#             type: "number"
#             required: False
#           max_value:
#             type: "number"
#             required: False
#           initial_value:
#             type: "any"
#             required: False
#           mappings:
#            type: "seq"
#            required: True
#            allowempty: False
#            sequence:
#               - type: "map"
#                 allowempty: True
#                 mapping:
#                   type:
#                     type: "str"
#                   intent:
#                     type: "any"
#                   not_intent:
#                     type: "any"
#                   entity:
#                     type: "str"
#                   role:
#                     type: "str"
#                   group:
#                     type: "str"
#                   value:
#                     type: "any"
#                   action:
#                     type: "str"
#                   conditions:
#                     type: "seq"
#                     sequence:
#                       - type: "map"
#                         mapping:
#                           active_loop:
#                             type: "str"
#                             nullable: True
#                           requested_slot:
#                             type: "str"
#   forms:
#     type: "map"
#     required: False
#     mapping:
#       regex;([A-Za-z]+):
#         type: "map"
#         mapping:
#           required_slots:
#             type: "seq"
#             sequence:
#               - type: str
#             required: False
#             allowempty: True
#           ignored_intents:
#             type: any
#   config:
#     type: "map"
#     allowempty: True
#     mapping:
#       store_entities_as_slots:
#         type: "bool"
#   session_config:
#     type: "map"
#     allowempty: True
#     mapping:
#       session_expiration_time:
#         type: "number"
#         range:
#           min: 0
#       carry_over_slots_to_new_session:
#         type: "bool"




        # --------------------------------- SOME NOTES -----------------------------------------
#          mappings:
    # - type: from_entity
    #   entity: number
    #   intent: [inform, request_restaurant]

#     mappings:
    # - type: from_entity
    #   entity: seating
    # - type: from_intent
    #   intent: affirm
    #   value: true
    #   conditions:
    #   - active_loop: restaurant_form
    #     requested_slot: outdoor_seating
    
# --------------------------------- SOME NOTES -----------------------------------------