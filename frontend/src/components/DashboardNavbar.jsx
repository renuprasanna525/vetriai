import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { getNotifications } from "../services/notificationService";
import { getCurrentUser } from "../services/authService";

function DashboardNavbar() {
    const navigate = useNavigate();
    const location = useLocation();

    const [unreadCount, setUnreadCount] = useState(0);

    const [currentUser, setCurrentUser] = useState({
        name: "User",
        role: "Employee",
    });

    async function loadUnreadCount() {
        try {
            const accessToken = localStorage.getItem("access_token");

            if (!accessToken) {
                setUnreadCount(0);
                return;
            }

            const notifications = await getNotifications();

            const unreadNotifications = notifications.filter(
                (notification) => !notification.is_read
            );

            setUnreadCount(unreadNotifications.length);

        } catch (error) {
            console.error(
                "Failed to load notification count:",
                error
            );

            setUnreadCount(0);
        }
    }

    async function loadCurrentUser() {
        try {
            const user = await getCurrentUser();

            setCurrentUser({
                name: user.name || user.username || "User",
                role: user.role || "Employee",
            });

        } catch (error) {
            console.error(
                "Failed to load current user:",
                error
            );
        }
    }

    useEffect(() => {
        loadUnreadCount();
        loadCurrentUser();

        const interval = setInterval(() => {
            loadUnreadCount();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    return (
        <header className="dashboard-header">

            {/* Page Information */}
            <div>
                <h5 className="mb-1 fw-bold">
                    {getPageTitle(location.pathname)}
                </h5>

                <small className="text-muted">
                    Vetri AI Multi-Agent Platform
                </small>
            </div>


            {/* Right Side */}
            <div className="d-flex align-items-center gap-3">

                {/* Notifications */}
                <button
                    type="button"
                    className="header-notification"
                    onClick={() => navigate("/notifications")}
                    title="Notifications"
                >
                    <i className="bi bi-bell"></i>

                    {unreadCount > 0 && (
                        <span className="notification-badge">
                            {unreadCount}
                        </span>
                    )}
                </button>


                {/* Current User */}
                <div className="header-user">

                    <div className="header-user-icon">
                        <i className="bi bi-person-fill"></i>
                    </div>

                    <div className="d-none d-md-block">

                        <div className="fw-semibold">
                            {currentUser.name}
                        </div>

                        <small className="text-muted">
                            {currentUser.role}
                        </small>

                    </div>

                </div>

            </div>

        </header>
    );
}


function getPageTitle(path) {

    const titles = {
        "/dashboard": "Dashboard",
        "/ai-chat": "AI Chat",
        "/user-roles": "User Roles",
        "/permissions": "Permissions",
        "/agent-orchestrator": "Agent Orchestrator",
        "/approvals": "Approvals",
        "/notifications": "Notifications",
    };

    return titles[path] || "Vetri AI";
}


export default DashboardNavbar;