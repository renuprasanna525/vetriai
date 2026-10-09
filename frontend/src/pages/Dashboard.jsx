import { useEffect, useState } from 'react';

import StatCard from '../components/StatCard';
import DashboardCard from '../components/DashboardCard';
import ActivityList from '../components/ActivityList';

import { getDashboard } from '../services/api';


function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');


  useEffect(() => {
    loadDashboard();
  }, []);


  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError('');

      const data = await getDashboard();

      if (!data || !data.dashboard) {
        throw new Error('Dashboard data is unavailable.');
      }

      setDashboard(data.dashboard);

    } catch (err) {
      console.error('Dashboard error:', err);

      setError(
        err.message || 'Failed to load dashboard.'
      );

    } finally {
      setLoading(false);
    }
  };


  /*
   * Loading state
   */
  if (loading) {
    return (
      <main className="container-fluid px-4 py-4">
        <div className="dashboard-loading">

          <div className="dashboard-loading-icon">
            <i className="bi bi-bar-chart-line"></i>
          </div>

          <div className="spinner-border text-primary mt-3" role="status">
            <span className="visually-hidden">
              Loading...
            </span>
          </div>

          <p className="text-muted mt-3 mb-0">
            Loading dashboard...
          </p>

        </div>
      </main>
    );
  }


  /*
   * Error state
   */
  if (error) {
    return (
      <main className="container-fluid px-4 py-4">

        <div
          className="alert alert-danger"
          role="alert"
        >
          <i className="bi bi-exclamation-triangle me-2"></i>

          {error}
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={loadDashboard}
        >
          <i className="bi bi-arrow-clockwise me-2"></i>

          Try Again
        </button>

      </main>
    );
  }


  /*
   * No dashboard data
   */
  if (!dashboard) {
    return (
      <main className="container-fluid px-4 py-4">
        <div className="alert alert-warning">
          Dashboard data is not available.
        </div>
      </main>
    );
  }


  /*
   * Backend dashboard sections
   */
  const finance = dashboard.finance || {};
  const sales = dashboard.sales || {};
  const customers = dashboard.customers || {};
  const followups = dashboard.followups || {};

  const projects = dashboard.projects || {};
  const projectStatus = dashboard.project_status || {};
  const delayedProjects = dashboard.delayed_projects || {};

  const deadlines = dashboard.deadlines || {};
  const tasks = dashboard.tasks || {};

  const employees = dashboard.employees || {};
  const employeesOnLeave =
    dashboard.employees_on_leave || {};

  const pendingOrders =
    dashboard.pending_orders || {};


  /*
   * Employee statistics
   */
  const totalEmployees =
    Number(employees.total_employees) || 0;

  const totalOnLeave =
    Number(employeesOnLeave.total_on_leave) || 0;

  const activeEmployees = Math.max(
    totalEmployees - totalOnLeave,
    0
  );


  /*
   * Task information
   */
  const taskList = Array.isArray(tasks.tasks)
    ? tasks.tasks
    : [];

  const pendingTaskList = taskList.filter(
    (task) => task?.status !== 'Completed'
  );

  const pendingTaskCount =
    pendingTaskList.length;


  /*
   * Follow-up information
   */
  const pendingFollowups =
    Array.isArray(followups.pending_followups)
      ? followups.pending_followups
      : [];


  /*
   * Business activity
   *
   * Only actual backend information is used.
   * No artificial timestamps are created.
   */
  const activities = [];


  const leadCount =
    Number(sales.new_leads) || 0;


  if (leadCount > 0) {
    activities.push({
      id: 'leads',
      title: 'New leads',
      description:
        `${leadCount} new leads are currently available.`,
      time: 'Current data',
    });
  }


  const delayedProjectCount =
    Number(delayedProjects.total_delayed) || 0;


  if (delayedProjectCount > 0) {
    const delayedProject =
      Array.isArray(
        delayedProjects.delayed_projects
      )
        ? delayedProjects.delayed_projects[0]
        : null;

    activities.push({
      id: 'delayed-project',
      title: 'Delayed project',
      description: delayedProject
        ? `${delayedProject.name} is delayed by ${delayedProject.delay_days} days.`
        : `${delayedProjectCount} projects are delayed.`,
      time: 'Current data',
    });
  }


  if (pendingTaskCount > 0) {
    const pendingTask =
      pendingTaskList[0];

    activities.push({
      id: 'pending-task',
      title: 'Pending task',
      description: pendingTask?.task
        ? `${pendingTask.task} is ${pendingTask.status}.`
        : `${pendingTaskCount} tasks require attention.`,
      time: 'Current data',
    });
  }


  const pendingOrderCount =
    Number(pendingOrders.pending_orders) || 0;


  if (pendingOrderCount > 0) {
    activities.push({
      id: 'pending-orders',
      title: 'Pending orders',
      description:
        `${pendingOrderCount} orders are awaiting action.`,
      time: 'Current data',
    });
  }


  /*
   * Business risks
   */
  const risks = [];


  if (delayedProjectCount > 0) {
    risks.push({
      id: 'delayed-projects',
      name:
        `${delayedProjectCount} delayed project(s)`,
      level: 'High',
    });
  }


  if (pendingFollowups.length > 0) {
    risks.push({
      id: 'pending-followups',
      name:
        `${pendingFollowups.length} pending customer follow - up(s)`,
      level: 'Medium',
    });
  }


  if (pendingOrderCount > 0) {
    risks.push({
      id: 'pending-orders',
      name:
        `${pendingOrderCount} pending order(s)`,
      level: 'Medium',
    });
  }


  /*
   * Format Indian currency
   */
  const formatCurrency = (value) => {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return '₹0';
    }

    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(numericValue);
  };


  /*
   * Format project deadline
   */
  const formatDate = (dateString) => {
    if (!dateString) {
      return '-';
    }

    const date = new Date(
      `${dateString} T00:00:00`
    );

    if (Number.isNaN(date.getTime())) {
      return '-';
    }

    return date.toLocaleDateString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
      }
    );
  };


  return (
    <main className="container-fluid px-4 py-4">

      {/* Header */}
      <div className="mb-4">

        <h2 className="fw-bold">
          Welcome, Renuka
        </h2>

        <p className="text-muted mb-0">
          Here's an overview of your business operations.
        </p>

      </div>


      {/* Main Statistics */}
      <div className="row">

        <StatCard
          title="Revenue"
          value={formatCurrency(
            finance.total_revenue
          )}
          icon="bi-currency-rupee"
          description={
            `Expenses: ${formatCurrency(
              finance.total_expenses
            )
            } `
          }
        />


        <StatCard
          title="Leads"
          value={Number(sales.total_leads) || 0}
          icon="bi-person-plus"
          description={
            `${Number(sales.new_leads) || 0} new leads`
          }
        />


        <StatCard
          title="Projects"
          value={
            Number(projects.total_projects) || 0
          }
          icon="bi-kanban"
          description={
            `${Number(projectStatus.active_projects) || 0} active projects`
          }
        />


        <StatCard
          title="Customers"
          value={
            Number(customers.total_customers) || 0
          }
          icon="bi-people"
          description="Active customers"
        />

      </div>


      {/* Employee / Operations Statistics */}
      <div className="row">

        <StatCard
          title="Employees"
          value={totalEmployees}
          icon="bi-person-badge"
          description={
            `${activeEmployees} currently active`
          }
        />


        <StatCard
          title="Leave"
          value={totalOnLeave}
          icon="bi-calendar-check"
          description="Employees on leave"
        />


        <StatCard
          title="Workload"
          value={dashboard.workload?.active_tasks ?? 0}
          icon="bi-bar-chart"
          description={`${dashboard.workload?.active_tasks ?? 0} active tasks`}
        />


        <StatCard
          title="Pending Tasks"
          value={pendingTaskCount}
          icon="bi-list-task"
          description="Tasks awaiting action"
        />

      </div>
      {/* Project Status Analytics */}
      <div className="row g-4 mb-4">

        <div className="col-12">

          <DashboardCard title="Project Status">

            <div className="row text-center">

              <div className="col-12 col-md-4 mb-3 mb-md-0">
                <div className="p-3 border rounded project-status-card">

                  <div className="dashboard-project-status-icon">
                    <i className="bi bi-play-circle"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(projectStatus.active_projects) || 0}
                  </h3>

                  <div className="text-muted">
                    Active Projects
                  </div>

                </div>
              </div>

              <div className="col-12 col-md-4 mb-3 mb-md-0">
                <div className="p-3 border rounded project-status-card">

                  <div className="dashboard-project-status-icon">
                    <i className="bi bi-check-circle"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(projectStatus.completed_projects) || 0}
                  </h3>

                  <div className="text-muted">
                    Completed Projects
                  </div>

                </div>
              </div>

              <div className="col-12 col-md-4">
                <div className="p-3 border rounded project-status-card">

                  <div className="dashboard-project-status-icon">
                    <i className="bi bi-exclamation-circle"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(projectStatus.delayed_projects) || 0}
                  </h3>

                  <div className="text-muted">
                    Delayed Projects
                  </div>

                </div>
              </div>

            </div>

          </DashboardCard>

        </div>

      </div>
      {/* Financial Analytics */}
      <div className="row g-4 mb-4">

        <div className="col-12">

          <DashboardCard title="Financial Overview">

            <div className="row text-center">

              <div className="col-12 col-md-4 mb-3 mb-md-0">
                <div className="p-3 border rounded financial-card">

                  <div className="financial-icon">
                    <i className="bi bi-arrow-down-left"></i>
                  </div>

                  <h3 className="mb-1">
                    {formatCurrency(finance.total_revenue)}
                  </h3>

                  <div className="text-muted">
                    Total Revenue
                  </div>

                </div>
              </div>

              <div className="col-12 col-md-4 mb-3 mb-md-0">
                <div className="p-3 border rounded financial-card">

                  <div className="financial-icon">
                    <i className="bi bi-arrow-up-right"></i>
                  </div>

                  <h3 className="mb-1">
                    {formatCurrency(finance.total_expenses)}
                  </h3>

                  <div className="text-muted">
                    Total Expenses
                  </div>

                </div>
              </div>

              <div className="col-12 col-md-4">
                <div className="p-3 border rounded financial-card">

                  <div className="financial-icon">
                    <i className="bi bi-graph-up-arrow"></i>
                  </div>

                  <h3 className="mb-1">
                    {formatCurrency(finance.net_profit)}
                  </h3>

                  <div className="text-muted">
                    Net Profit
                  </div>

                </div>
              </div>

            </div>

          </DashboardCard>

        </div>

      </div>
      {/* Sales Analytics */}
      <div className="row g-4 mb-4">

        <div className="col-12">

          <DashboardCard title="Sales Overview">

            <div className="row text-center">

              <div className="col-6 col-lg-3 mb-3 mb-lg-0">
                <div className="p-3 border rounded sales-card">

                  <div className="sales-icon">
                    <i className="bi bi-person-plus"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(sales.total_leads) || 0}
                  </h3>

                  <div className="text-muted">
                    Total Leads
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3 mb-3 mb-lg-0">
                <div className="p-3 border rounded sales-card">

                  <div className="sales-icon">
                    <i className="bi bi-person-check"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(sales.new_leads) || 0}
                  </h3>

                  <div className="text-muted">
                    New Leads
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3">
                <div className="p-3 border rounded sales-card">

                  <div className="sales-icon">
                    <i className="bi bi-clock-history"></i>
                  </div>

                  <h3 className="mb-1">
                    {pendingFollowups.length}
                  </h3>

                  <div className="text-muted">
                    Pending Follow-ups
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3">
                <div className="p-3 border rounded sales-card">

                  <div className="sales-icon">
                    <i className="bi bi-cart-check"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(pendingOrders.pending_orders) || 0}
                  </h3>

                  <div className="text-muted">
                    Pending Orders
                  </div>

                </div>
              </div>

            </div>

          </DashboardCard>

        </div>

      </div>

      {/* Employee & HR Analytics */}
      <div className="row g-4 mb-4">

        <div className="col-12">

          <DashboardCard title="Employee & HR Overview">

            <div className="row text-center">

              <div className="col-6 col-lg-3 mb-3 mb-lg-0">
                <div className="p-3 border rounded hr-card">

                  <div className="hr-icon">
                    <i className="bi bi-people"></i>
                  </div>

                  <h3 className="mb-1">
                    {totalEmployees}
                  </h3>

                  <div className="text-muted">
                    Total Employees
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3 mb-3 mb-lg-0">
                <div className="p-3 border rounded hr-card">

                  <div className="hr-icon">
                    <i className="bi bi-person-check"></i>
                  </div>

                  <h3 className="mb-1">
                    {activeEmployees}
                  </h3>

                  <div className="text-muted">
                    Active Employees
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3">
                <div className="p-3 border rounded hr-card">

                  <div className="hr-icon">
                    <i className="bi bi-calendar-x"></i>
                  </div>

                  <h3 className="mb-1">
                    {totalOnLeave}
                  </h3>

                  <div className="text-muted">
                    On Leave
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3">
                <div className="p-3 border rounded hr-card">

                  <div className="hr-icon">
                    <i className="bi bi-calendar-check"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(
                      dashboard.attendance?.present
                    ) || 0}
                  </h3>

                  <div className="text-muted">
                    Present Today
                  </div>

                </div>
              </div>

            </div>

          </DashboardCard>

        </div>

      </div>
      {/* Task & Workload Analytics */}
      <div className="row g-4 mb-4">

        <div className="col-12">

          <DashboardCard title="Task & Workload Overview">

            <div className="row text-center">

              <div className="col-6 col-lg-3 mb-3 mb-lg-0">
                <div className="p-3 border rounded workload-card">

                  <div className="workload-icon">
                    <i className="bi bi-list-task"></i>
                  </div>

                  <h3 className="mb-1">
                    {dashboard.workload?.total_tasks ?? 0}
                  </h3>

                  <div className="text-muted">
                    Total Tasks
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3 mb-3 mb-lg-0">
                <div className="p-3 border rounded workload-card">

                  <div className="workload-icon">
                    <i className="bi bi-hourglass-split"></i>
                  </div>

                  <h3 className="mb-1">
                    {dashboard.workload?.active_tasks ?? 0}
                  </h3>

                  <div className="text-muted">
                    Active Tasks
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3">
                <div className="p-3 border rounded workload-card">

                  <div className="workload-icon">
                    <i className="bi bi-check2-circle"></i>
                  </div>

                  <h3 className="mb-1">
                    {dashboard.workload?.completed_tasks ?? 0}
                  </h3>

                  <div className="text-muted">
                    Completed Tasks
                  </div>

                </div>
              </div>

              <div className="col-6 col-lg-3">
                <div className="p-3 border rounded workload-card">

                  <div className="workload-icon">
                    <i className="bi bi-exclamation-triangle"></i>
                  </div>

                  <h3 className="mb-1">
                    {pendingTaskCount}
                  </h3>

                  <div className="text-muted">
                    Pending Tasks
                  </div>

                </div>
              </div>

            </div>

          </DashboardCard>

        </div>

      </div>
      {/* Customer Analytics */}
      <div className="row g-4 mb-4">

        <div className="col-12">

          <DashboardCard title="Customer Overview">

            <div className="row text-center">

              <div className="col-12 col-md-4 mb-3 mb-md-0">
                <div className="p-3 border rounded customer-card">

                  <div className="customer-icon">
                    <i className="bi bi-people"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(customers.total_customers) || 0}
                  </h3>

                  <div className="text-muted">
                    Total Customers
                  </div>

                </div>
              </div>

              <div className="col-12 col-md-4 mb-3 mb-md-0">
                <div className="p-3 border rounded customer-card">

                  <div className="customer-icon">
                    <i className="bi bi-person-check"></i>
                  </div>

                  <h3 className="mb-1">
                    {Number(customers.total_customers) || 0}
                  </h3>

                  <div className="text-muted">
                    Active Customers
                  </div>

                </div>
              </div>

              <div className="col-12 col-md-4">
                <div className="p-3 border rounded customer-card">

                  <div className="customer-icon">
                    <i className="bi bi-person-lines-fill"></i>
                  </div>

                  <h3 className="mb-1">
                    {pendingFollowups.length}
                  </h3>

                  <div className="text-muted">
                    Customers With Follow-ups
                  </div>

                </div>
              </div>

            </div>

          </DashboardCard>

        </div>

      </div>

      {/* Business Activity + Pending Tasks */}
      <div className="row g-4 mb-4">

        {/* Business Activity */}
        <div className="col-12 col-lg-8">

          <DashboardCard title="Business Activity">

            {activities.length > 0 ? (

              <ActivityList
                activities={activities}
              />

            ) : (

              <p className="text-muted mb-0">
                No current business activity available.
              </p>

            )}

          </DashboardCard>

        </div>


        {/* Pending Tasks */}
        <div className="col-12 col-lg-4">

          <DashboardCard title="Pending Tasks">

            {pendingTaskList.length > 0 ? (

              <ul className="list-group list-group-flush">

                {pendingTaskList.map(
                  (task, index) => (

                    <li
                      key={
                        task.id ??
                        task.task ??
                        `task - ${index} `
                      }
                      className="list-group-item px-0"
                    >

                      <i className="bi bi-check2-square text-primary me-2"></i>

                      <strong>
                        {task.task || 'Unnamed task'}
                      </strong>

                      <div className="small text-muted ms-4">
                        {task.project || 'Project unavailable'}
                        {' · '}
                        {task.status || 'Status unavailable'}
                      </div>

                    </li>

                  )
                )}

              </ul>

            ) : (

              <p className="text-muted mb-0">
                No pending tasks.
              </p>

            )}

          </DashboardCard>

        </div>

      </div>


      {/* Risks + Deadlines */}
      <div className="row g-4">

        {/* Risks */}
        <div className="col-12 col-lg-6">

          <DashboardCard title="Risks">

            {risks.length > 0 ? (

              <div className="list-group list-group-flush">

                {risks.map(
                  (risk) => (

                    <div
                      key={risk.id}
                      className="list-group-item px-0 d-flex justify-content-between align-items-center"
                    >

                      <span>
                        {risk.name}
                      </span>

                      <span
                        className={
                          `badge ${risk.level === 'High'
                            ? 'bg-danger'
                            : risk.level === 'Medium'
                              ? 'bg-warning text-dark'
                              : 'bg-success'
                          } `
                        }
                      >
                        {risk.level}
                      </span>

                    </div>

                  )
                )}

              </div>

            ) : (

              <p className="text-muted mb-0">
                No current risks identified.
              </p>

            )}

          </DashboardCard>

        </div>


        {/* Project Deadlines */}
        <div className="col-12 col-lg-6">

          <DashboardCard title="Project Deadlines">

            {Array.isArray(
              deadlines.deadlines
            ) &&
              deadlines.deadlines.length > 0 ? (

              <div className="list-group list-group-flush">

                {deadlines.deadlines.map(
                  (deadline, index) => (

                    <div
                      key={
                        deadline.id ??
                        `${deadline.project} -${deadline.deadline} -${index} `
                      }
                      className="list-group-item px-0 d-flex justify-content-between align-items-center"
                    >

                      <span>
                        {deadline.project ||
                          'Project unavailable'}
                      </span>

                      <strong>
                        {formatDate(
                          deadline.deadline
                        )}
                      </strong>

                    </div>

                  )
                )}

              </div>

            ) : (

              <p className="text-muted mb-0">
                No project deadlines available.
              </p>

            )}

          </DashboardCard>

        </div>

      </div>

    </main>
  );
}


export default Dashboard;

