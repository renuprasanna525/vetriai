import { useEffect, useState } from "react";
import { getCurrentUser } from "../services/authService";
import {
    getApprovals,
    approveAction,
    editApproval,
    cancelAction,
} from "../services/approvalService";

import "./Approvals.css";

function Approvals() {
    const [approvals, setApprovals] = useState([]);

    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);

    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [currentUser, setCurrentUser] = useState(null);

    async function loadApprovals() {
        try {
            setLoading(true);
            setError("");

            const result = await getApprovals("pending");

            setApprovals(result.actions || []);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        async function initializePage() {
            try {
                const user = await getCurrentUser();
                setCurrentUser(user);
            } catch (err) {
                setError(err.message);
            }

            await loadApprovals();
        }

        initializePage();
    }, []);

    async function handleApprove(actionId) {
        try {
            setActionLoading(actionId);
            setError("");
            setMessage("");

            const result = await approveAction(actionId);

            setMessage(
                result.execution
                    ? "Action approved and executed successfully."
                    : "Action approved successfully."
            );

            await loadApprovals();

        } catch (err) {
            setError(err.message);
        } finally {
            setActionLoading(null);
        }
    }

    async function handleEdit(approval) {
        const currentParameters = approval.parameters || {};

        const to = window.prompt(
            "Recipient:",
            currentParameters.to || ""
        );

        if (to === null) {
            return;
        }

        const subject = window.prompt(
            "Subject:",
            currentParameters.subject || ""
        );

        if (subject === null) {
            return;
        }

        const messageText = window.prompt(
            "Message:",
            currentParameters.message || ""
        );

        if (messageText === null) {
            return;
        }

        try {
            setActionLoading(approval.action_id);
            setError("");
            setMessage("");

            await editApproval(
                approval.action_id,
                {
                    to,
                    subject,
                    message: messageText,
                }
            );

            setMessage(
                `Approval #${approval.action_id} updated successfully.`
            );

            await loadApprovals();

        } catch (err) {
            setError(err.message);
        } finally {
            setActionLoading(null);
        }
    }

    async function handleCancel(actionId) {
        const confirmed = window.confirm(
            "Are you sure you want to cancel this approval?"
        );

        if (!confirmed) {
            return;
        }

        try {
            setActionLoading(actionId);
            setError("");
            setMessage("");

            await cancelAction(actionId);

            setMessage(
                `Approval #${actionId} cancelled successfully.`
            );

            await loadApprovals();

        } catch (err) {
            setError(err.message);
        } finally {
            setActionLoading(null);
        }
    }

    return (
        <div className="approvals-page">
            <div className="container-fluid approvals-container">

                {/* PAGE HEADER */}
                <div className="approvals-page-header">

                    <div className="approvals-title-area">

                        <div className="approvals-title-icon">
                            <i className="bi bi-shield-check"></i>
                        </div>

                        <div>
                            <h2 className="approvals-page-title">
                                Approvals
                            </h2>

                            <p className="approvals-page-subtitle">
                                Review and manage sensitive AI actions requiring approval.
                            </p>
                        </div>

                    </div>

                    <button
                        type="button"
                        className="btn btn-outline-primary approvals-refresh-btn"
                        onClick={loadApprovals}
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span
                                    className="spinner-border spinner-border-sm me-2"
                                    role="status"
                                ></span>
                                Loading...
                            </>
                        ) : (
                            <>
                                <i className="bi bi-arrow-clockwise me-1"></i>
                                Refresh
                            </>
                        )}
                    </button>

                </div>

                {/* SUCCESS */}
                {message && (
                    <div className="alert alert-success approvals-alert">
                        <i className="bi bi-check-circle me-2"></i>
                        <span>{message}</span>
                    </div>
                )}

                {/* ERROR */}
                {error && (
                    <div className="alert alert-danger approvals-alert">
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        <span>{error}</span>
                    </div>
                )}

                {/* LOADING */}
                {loading ? (

                    <div className="approvals-empty-state">

                        <div
                            className="spinner-border text-primary"
                            role="status"
                        >
                            <span className="visually-hidden">
                                Loading...
                            </span>
                        </div>

                        <p className="text-muted mt-3 mb-0">
                            Loading approvals...
                        </p>

                    </div>

                ) : approvals.length === 0 ? (

                    /* EMPTY STATE */

                    <div className="card approvals-card">

                        <div className="card-body approvals-empty-state">

                            <div className="approvals-empty-icon">
                                <i className="bi bi-check2-circle"></i>
                            </div>

                            <h5 className="mt-3 mb-2">
                                No Pending Approvals
                            </h5>

                            <p className="text-muted mb-0">
                                There are currently no actions waiting for approval.
                            </p>

                        </div>

                    </div>

                ) : (

                    /* APPROVAL LIST */

                    <div className="approvals-list">

                        {approvals.map((approval) => {

                            const parameters =
                                approval.parameters || {};
                            const isApprover =
                                ["admin", "manager"].includes(currentUser?.role_code);

                            const isRequester =
                                currentUser?.id != null &&
                                approval.requester_id != null &&
                                Number(currentUser.id) === Number(approval.requester_id);

                            const isPending =
                                approval.status === "pending";

                            const canApprove =
                                isApprover && isPending;

                            const canEditOrCancel =
                                isRequester && isPending;

                            const isProcessing =
                                actionLoading === approval.action_id;

                            return (
                                <div
                                    className="card approvals-card"
                                    key={approval.action_id}
                                >

                                    {/* CARD HEADER */}
                                    <div className="approvals-card-header">

                                        <div className="approval-heading">

                                            <div className="approval-warning-icon">
                                                <i className="bi bi-exclamation-circle"></i>
                                            </div>

                                            <div className="approval-heading-content">

                                                <h5>
                                                    Approval #{approval.action_id}
                                                </h5>

                                                <small>
                                                    Sensitive AI action requires human approval
                                                </small>

                                            </div>

                                        </div>

                                        <span className="badge text-bg-warning approval-status">
                                            {approval.status}
                                        </span>

                                    </div>

                                    {/* CARD BODY */}
                                    <div className="card-body approvals-card-body">

                                        {/* ACTION INFORMATION */}
                                        <div className="row g-3 mb-4">

                                            <div className="col-12 col-md-4">
                                                <div className="approval-info-box">

                                                    <span className="approval-info-label">
                                                        Agent
                                                    </span>

                                                    <div className="approval-info-value">
                                                        <i className="bi bi-robot"></i>
                                                        <span>
                                                            {approval.agent}
                                                        </span>
                                                    </div>

                                                </div>
                                            </div>

                                            <div className="col-12 col-md-4">
                                                <div className="approval-info-box">

                                                    <span className="approval-info-label">
                                                        Tool
                                                    </span>

                                                    <div className="approval-info-value">
                                                        <i className="bi bi-tools"></i>
                                                        <span>
                                                            {approval.tool}
                                                        </span>
                                                    </div>

                                                </div>
                                            </div>

                                            <div className="col-12 col-md-4">
                                                <div className="approval-info-box">

                                                    <span className="approval-info-label">
                                                        Action
                                                    </span>

                                                    <div className="approval-info-value">
                                                        <i className="bi bi-lightning-charge"></i>
                                                        <span>
                                                            {approval.action}
                                                        </span>
                                                    </div>

                                                </div>
                                            </div>

                                        </div>

                                        {/* PARAMETERS */}
                                        <div className="approval-parameters">

                                            <div className="approval-parameters-header">

                                                <div className="approval-parameters-icon">
                                                    <i className="bi bi-sliders"></i>
                                                </div>

                                                <div>
                                                    <h6>
                                                        Action Parameters
                                                    </h6>

                                                    <small>
                                                        Details submitted for approval
                                                    </small>
                                                </div>

                                            </div>

                                            <div className="approval-parameters-content">

                                                {parameters.to && (
                                                    <div className="approval-parameter-row">
                                                        <span className="parameter-label">
                                                            Recipient
                                                        </span>

                                                        <span className="parameter-value">
                                                            {parameters.to}
                                                        </span>
                                                    </div>
                                                )}

                                                {parameters.subject && (
                                                    <div className="approval-parameter-row">
                                                        <span className="parameter-label">
                                                            Subject
                                                        </span>

                                                        <span className="parameter-value">
                                                            {parameters.subject}
                                                        </span>
                                                    </div>
                                                )}

                                                {parameters.message && (
                                                    <div className="approval-message-row">

                                                        <span className="parameter-label">
                                                            Message
                                                        </span>

                                                        <div className="approval-message-value">
                                                            {parameters.message}
                                                        </div>

                                                    </div>
                                                )}

                                                {!parameters.to &&
                                                    !parameters.subject &&
                                                    !parameters.message && (
                                                        <pre className="approval-json">
                                                            {JSON.stringify(
                                                                parameters,
                                                                null,
                                                                2
                                                            )}
                                                        </pre>
                                                    )}

                                            </div>

                                        </div>

                                        {/* ACTION BUTTONS */}
                                        <div className="approval-actions">

                                            {/* APPROVE: Only managers and admins */}
                                            {canApprove && (
                                                <button
                                                    type="button"
                                                    className="btn btn-success"
                                                    onClick={() =>
                                                        handleApprove(
                                                            approval.action_id
                                                        )
                                                    }
                                                    disabled={isProcessing}
                                                >
                                                    {isProcessing ? (
                                                        <>
                                                            <span
                                                                className="spinner-border spinner-border-sm me-2"
                                                                role="status"
                                                            ></span>

                                                            Processing...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <i className="bi bi-check-lg me-1"></i>
                                                            Approve
                                                        </>
                                                    )}
                                                </button>
                                            )}

                                            {/* EDIT: Only the original requester */}
                                            {canEditOrCancel && (
                                                <button
                                                    type="button"
                                                    className="btn btn-warning"
                                                    onClick={() =>
                                                        handleEdit(approval)
                                                    }
                                                    disabled={isProcessing}
                                                >
                                                    <i className="bi bi-pencil me-1"></i>
                                                    Edit
                                                </button>
                                            )}

                                            {/* CANCEL: Only the original requester */}
                                            {canEditOrCancel && (
                                                <button
                                                    type="button"
                                                    className="btn btn-danger"
                                                    onClick={() =>
                                                        handleCancel(
                                                            approval.action_id
                                                        )
                                                    }
                                                    disabled={isProcessing}
                                                >
                                                    <i className="bi bi-x-lg me-1"></i>
                                                    Cancel
                                                </button>
                                            )}

                                        </div>

                                    </div>

                                </div>
                            );
                        })}

                    </div>
                )}

            </div>
        </div>
    );
}

export default Approvals;