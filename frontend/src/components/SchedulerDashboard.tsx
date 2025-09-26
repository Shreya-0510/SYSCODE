import React from 'react';
import { Calendar, Clock, Users, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';

const SchedulerDashboard = () => {
  const projects = [
    {
      id: 'PRJ-001',
      name: 'Substation Mumbai North',
      type: 'Substation',
      status: 'In Progress',
      progress: 65,
      startDate: '2024-01-15',
      expectedEnd: '2024-06-30',
      actualEnd: '2024-07-15',
      risk: 'Medium',
      team: 12
    },
    {
      id: 'PRJ-002',
      name: 'Underground Cable Pune',
      type: 'Underground Cable',
      status: 'Planning',
      progress: 15,
      startDate: '2024-03-01',
      expectedEnd: '2024-08-15',
      actualEnd: '-',
      risk: 'Low',
      team: 8
    },
    {
      id: 'PRJ-003',
      name: 'Overhead Line Nashik',
      type: 'Overhead Line',
      status: 'Delayed',
      progress: 40,
      startDate: '2023-11-01',
      expectedEnd: '2024-04-30',
      actualEnd: '2024-08-30',
      risk: 'High',
      team: 15
    }
  ];

  const upcomingMilestones = [
    { project: 'PRJ-001', milestone: 'Foundation Complete', date: '2024-02-15', status: 'upcoming' },
    { project: 'PRJ-002', milestone: 'Material Procurement', date: '2024-02-20', status: 'upcoming' },
    { project: 'PRJ-003', milestone: 'Tower Installation', date: '2024-02-10', status: 'overdue' },
    { project: 'PRJ-001', milestone: 'Equipment Installation', date: '2024-03-01', status: 'upcoming' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Progress': return 'bg-blue-100 text-blue-800';
      case 'Planning': return 'bg-yellow-100 text-yellow-800';
      case 'Delayed': return 'bg-red-100 text-red-800';
      case 'Completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return 'text-green-600';
      case 'Medium': return 'text-yellow-600';
      case 'High': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Project Scheduler Dashboard</h1>
        <p className="text-gray-600">Monitor project timelines, milestones, and resource allocation</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
            <Calendar className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">On Schedule</p>
              <p className="text-2xl font-bold text-green-600">2</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Delayed</p>
              <p className="text-2xl font-bold text-red-600">1</p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Resources</p>
              <p className="text-2xl font-bold text-gray-900">35</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>
      </div>

      {/* Projects Overview */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Projects Overview</h2>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Project</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Progress</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Timeline</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Risk</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Team</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div>
                      <div className="font-medium text-gray-900">{project.name}</div>
                      <div className="text-sm text-gray-500">{project.id} • {project.type}</div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                      {project.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${project.progress}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{project.progress}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="text-sm">
                      <div className="text-gray-900">{project.startDate} - {project.expectedEnd}</div>
                      {project.actualEnd !== '-' && (
                        <div className="text-red-600">Actual: {project.actualEnd}</div>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`font-medium ${getRiskColor(project.risk)}`}>
                      {project.risk}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-900">{project.team}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upcoming Milestones */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Milestones</h2>
          
          <div className="space-y-4">
            {upcomingMilestones.map((milestone, index) => (
              <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                <div className={`w-3 h-3 rounded-full ${
                  milestone.status === 'overdue' ? 'bg-red-500' : 'bg-blue-500'
                }`}></div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{milestone.milestone}</div>
                  <div className="text-sm text-gray-600">{milestone.project}</div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-medium ${
                    milestone.status === 'overdue' ? 'text-red-600' : 'text-gray-900'
                  }`}>
                    {milestone.date}
                  </div>
                  {milestone.status === 'overdue' && (
                    <div className="text-xs text-red-600">Overdue</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Resource Allocation */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Resource Allocation</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Users className="h-4 w-4 text-blue-600" />
                </div>
                <span className="font-medium text-gray-900">Engineers</span>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-blue-600">12</div>
                <div className="text-xs text-gray-600">Active</div>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Clock className="h-4 w-4 text-green-600" />
                </div>
                <span className="font-medium text-gray-900">Technicians</span>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-green-600">18</div>
                <div className="text-xs text-gray-600">Active</div>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-orange-600" />
                </div>
                <span className="font-medium text-gray-900">Project Managers</span>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-orange-600">5</div>
                <div className="text-xs text-gray-600">Active</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchedulerDashboard;