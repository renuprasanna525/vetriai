import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getNotifications } from "../services/notificationService";
import { getCurrentUser } from "../services/authService";

function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();

    const [unreadCount, setUnreadCount] = useState(0);
    const [isOpen, setIsOpen] = useState(false);

    const [currentUser, setCurrentUser] = useState({
        name: "User",
        role: "Employee",
    });

    function isActive(path) {
        return location.pathname === path;
    }

    async function loadCurrentUser() {
        try {
            const accessToken = localStorage.getItem("access_token");

            if (!accessToken) {
                return;
            }

            const user = await getCurrentUser();

            setCurrentUser({
                name: user.name || user.username || "User",
                role: user.role || "Employee",
            });
        } catch (error) {
            console.error("Failed to load current user:", error);
        }
    }

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

    useEffect(() => {
        loadCurrentUser();
        loadUnreadCount();

        const interval = setInterval(() => {
            loadUnreadCount();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    function navItem(path, icon, label, badgeCount = 0) {
        return (
            <button
                type="button"
                className={`sidebar-link w-100 ${isActive(path) ? "active" : ""
                    }`}
                onClick={() => {
                    navigate(path);
                    setIsOpen(false);
                }}
            >
                <i className={`bi ${icon} me-3`}></i>

                <span className="flex-grow-1 text-start">
                    {label}
                </span>

                {badgeCount > 0 && (
                    <span className="badge bg-danger rounded-pill">
                        {badgeCount}
                    </span>
                )}
            </button>
        );
    }

    function handleLogout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        navigate("/login");
    }

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                type="button"
                className="mobile-menu-button"
                onClick={() => setIsOpen(true)}
                aria-label="Open navigation menu"
            >
                <i className="bi bi-list"></i>
            </button>

            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="sidebar-overlay"
                    onClick={() => setIsOpen(false)}
                ></div>
            )}

            <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>

                {/* Mobile Close Button */}
                <button
                    type="button"
                    className="sidebar-close"
                    onClick={() => setIsOpen(false)}
                    aria-label="Close navigation menu"
                >
                    <i className="bi bi-x-lg"></i>
                </button>

                {/* Brand */}
                <div
                    className="sidebar-brand"
                    onClick={() => {
                        navigate("/dashboard");
                        setIsOpen(false);
                    }}
                >
                    <div className="brand-title">
                        Vetri AI
                    </div>

                    <div className="brand-subtitle">
                        AI Operations
                    </div>
                </div>

                {/* Main */}
                <div className="sidebar-section">

                    <div className="sidebar-heading">
                        MAIN
                    </div>

                    {navItem(
                        "/dashboard",
                        "bi-grid-1x2-fill",
                        "Dashboard"
                    )}

                    {navItem(
                        "/ai-chat",
                        "bi-chat-dots-fill",
                        "AI Chat"
                    )}

                </div>

                {/* Management */}
                <div className="sidebar-section">

                    <div className="sidebar-heading">
                        MANAGEMENT
                    </div>

                    {navItem(
                        "/user-roles",
                        "bi-people-fill",
                        "User Roles"
                    )}

                    {navItem(
                        "/permissions",
                        "bi-shield-lock-fill",
                        "Permissions"
                    )}

                    {navItem(
                        "/agent-orchestrator",
                        "bi-diagram-3-fill",
                        "Agent Orchestrator"
                    )}

                    {navItem(
                        "/approvals",
                        "bi-check2-square",
                        "Approvals"
                    )}

                </div>

                {/* System */}
                <div className="sidebar-section">

                    <div className="sidebar-heading">
                        SYSTEM
                    </div>

                    {navItem(
                        "/notifications",
                        "bi-bell-fill",
                        "Notifications",
                        unreadCount
                    )}

                </div>

                {/* Bottom */}
                <div className="sidebar-bottom">

                    <div className="sidebar-user">

                        <div className="user-icon">
                            <i className="bi bi-person-fill"></i>
                        </div>

                        <div>
                            <div className="user-name">
                                {currentUser.name}
                            </div>

                            <div className="user-role">
                                {currentUser.role}
                            </div>
                        </div>

                    </div>

                    <button
                        type="button"
                        className="sidebar-logout"
                        onClick={handleLogout}
                    >
                        <i className="bi bi-box-arrow-right me-3"></i>
                        Logout
                    </button>

                </div>

            </aside>
        </>
    );
}

export default Sidebar;