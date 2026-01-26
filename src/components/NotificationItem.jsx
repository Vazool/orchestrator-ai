function NotificationItem({message,time,isRead}){

    return(
        <div className={isRead?"read" : "unread"} >
            <p>{message}</p>
            <small>{time}</small>
        </div>
       
    )
    
}
export default NotificationItem