import { useState, useEffect } from 'react';
import NotificationItem from './NotificationItem';

function NotificationsScreen() {
    const [alerts, setAlerts] = useState([]);

    // Fetch alerts from API
    const fetchAlerts = () => {
        fetch("http://localhost:5000/alerts")
            .then(res => res.json())
            .then(data => setAlerts(data))
            .catch(err => console.error("Error fetching alerts:", err));
    };

    
    useEffect(() => {
        fetchAlerts(); // initial fetch so nothing in the beginning 
        //This screen keeps checking for the API for new alerts
        const interval = setInterval(fetchAlerts, 5000);
        return () => clearInterval(interval); 
    }, []);

    const notificationList = alerts.map(alert => (
        <NotificationItem
            key={alert.id}
            message={alert.message}
            time={alert.time}
            isRead={alert.isRead}
        />
    ));

    return (
        <div>
            <h2>Notifications</h2>
            {notificationList.length === 0 ? <p>No alerts yet</p> : notificationList}
        </div>
    );
}

export default NotificationsScreen;
