connection: "thelook_events_redshift"

include: "/views/*.view.lkml"

#Moved Dashboard into a folder

explore: order_items {

  join: users {
    type: left_outer
    sql_on: ${order_items.user_id} = ${users.id} ;;
    relationship: many_to_one
  }

}
