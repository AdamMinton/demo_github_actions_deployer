connection: "thelook_events_redshift"

include: "/views/*.view.lkml"

#Moved Dashboard into a folder
#Moved dashbaord back to root folder, deleted folder
#moved dashboard back to new folder
#moved dashboard back to root folder, copied in same folder
#moved dashboard back to folder
#moved dashboard back to root
#Copied new dashboard
#lookml updaates
# added new dashboard
#just lookml changes
#jsut a small change
#renamed a dashboard


explore: order_items {

  join: users {
    type: left_outer
    sql_on: ${order_items.user_id} = ${users.id} ;;
    relationship: many_to_one
  }

}
