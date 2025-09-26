"""
API endpoints for geospatial data and mapping functionality
"""

from flask import request, jsonify
from flask_restful import Resource
from datetime import datetime
import logging
import json
from models.project_model import Project

logger = logging.getLogger(__name__)

class GeospatialResource(Resource):
    """
    Resource for geospatial data and map visualization
    """
    
    def get(self, data_type=None):
        """
        Get geospatial data
        
        Types: projects, assets, network, regions
        """
        try:
            if data_type == 'projects':
                return self._get_project_locations()
            elif data_type == 'assets':
                return self._get_asset_locations()
            elif data_type == 'network':
                return self._get_network_topology()
            elif data_type == 'regions':
                return self._get_regional_data()
            else:
                return self._get_comprehensive_geospatial_data()
                
        except Exception as e:
            logger.error(f"Error getting geospatial data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _get_project_locations(self):
        """Get project locations with coordinates and status"""
        try:
            from app import db
            
            # Get all projects with location data
            projects = Project.query.all()
            
            project_locations = []
            for project in projects:
                # Mock coordinates based on location - in production, would have actual coordinates
                coords = self._get_coordinates_for_location(project.location)
                
                project_data = {
                    'project_id': project.project_id,
                    'name': project.name,
                    'project_type': project.project_type,
                    'location': project.location,
                    'coordinates': coords,
                    'status': project.status,
                    'risk': project.risk,
                    'base_estimated_cost': project.base_estimated_cost,
                    'planned_timeline_months': project.planned_timeline_months,
                    'terrain_type': project.terrain_type,
                    'completion_percentage': self._calculate_completion_percentage(project),
                    'last_updated': project.updated_at.isoformat() if project.updated_at else None
                }
                
                # Add prediction data if available
                predictions = project.get_predictions()
                if predictions:
                    project_data['risk_score'] = predictions.get('risk_score', 0)
                    project_data['cost_overrun_probability'] = predictions.get('cost_overrun_probability', 0)
                    project_data['delay_probability'] = predictions.get('delay_probability', 0)
                
                project_locations.append(project_data)
            
            # Group projects by state for better visualization
            state_groups = {}
            for project in project_locations:
                if '/' in project['location']:
                    state = project['location'].split('/')[0]
                    if state not in state_groups:
                        state_groups[state] = []
                    state_groups[state].append(project)
            
            return {
                'success': True,
                'data': {
                    'projects': project_locations,
                    'state_groups': state_groups,
                    'total_projects': len(project_locations),
                    'bounds': self._calculate_map_bounds(project_locations)
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error getting project locations: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _get_asset_locations(self):
        """Get power grid asset locations"""
        
        # Mock asset data - in production would query asset database
        assets = [
            {
                'asset_id': 'SUB001',
                'name': 'Mumbai North 400kV Substation',
                'type': 'substation',
                'voltage_level': '400kV',
                'coordinates': {'lat': 19.0760, 'lng': 72.8777},
                'operational_status': 'active',
                'capacity_mw': 1200,
                'commissioned_date': '2018-03-15',
                'last_maintenance': '2023-11-20',
                'health_status': 'good'
            },
            {
                'asset_id': 'SUB002',
                'name': 'Delhi East 765kV Substation',
                'type': 'substation',
                'voltage_level': '765kV',
                'coordinates': {'lat': 28.6139, 'lng': 77.2090},
                'operational_status': 'active',
                'capacity_mw': 2000,
                'commissioned_date': '2020-08-10',
                'last_maintenance': '2023-12-05',
                'health_status': 'excellent'
            },
            {
                'asset_id': 'LINE001',
                'name': 'Mumbai-Pune 400kV Transmission Line',
                'type': 'transmission_line',
                'voltage_level': '400kV',
                'coordinates': [
                    {'lat': 19.0760, 'lng': 72.8777, 'point_type': 'start', 'location': 'Mumbai'},
                    {'lat': 18.5204, 'lng': 73.8567, 'point_type': 'end', 'location': 'Pune'}
                ],
                'operational_status': 'active',
                'length_km': 148,
                'capacity_mw': 800,
                'commissioned_date': '2019-12-01',
                'health_status': 'good'
            },
            {
                'asset_id': 'LINE002',
                'name': 'Delhi-Gurgaon 765kV Transmission Line',
                'type': 'transmission_line',
                'voltage_level': '765kV',
                'coordinates': [
                    {'lat': 28.6139, 'lng': 77.2090, 'point_type': 'start', 'location': 'Delhi'},
                    {'lat': 28.4595, 'lng': 77.0266, 'point_type': 'end', 'location': 'Gurgaon'}
                ],
                'operational_status': 'active',
                'length_km': 32,
                'capacity_mw': 1500,
                'commissioned_date': '2021-06-15',
                'health_status': 'excellent'
            },
            {
                'asset_id': 'GEN001',
                'name': 'Karnataka Solar Park Connection',
                'type': 'generating_station',
                'voltage_level': '220kV',
                'coordinates': {'lat': 15.3173, 'lng': 75.7139},
                'operational_status': 'active',
                'capacity_mw': 500,
                'generation_type': 'solar',
                'commissioned_date': '2022-01-20',
                'health_status': 'good'
            }
        ]
        
        # Group assets by type
        asset_groups = {}
        for asset in assets:
            asset_type = asset['type']
            if asset_type not in asset_groups:
                asset_groups[asset_type] = []
            asset_groups[asset_type].append(asset)
        
        return {
            'success': True,
            'data': {
                'assets': assets,
                'asset_groups': asset_groups,
                'summary': {
                    'total_assets': len(assets),
                    'substations': len([a for a in assets if a['type'] == 'substation']),
                    'transmission_lines': len([a for a in assets if a['type'] == 'transmission_line']),
                    'generating_stations': len([a for a in assets if a['type'] == 'generating_station']),
                    'total_capacity_mw': sum(a.get('capacity_mw', 0) for a in assets),
                    'active_assets': len([a for a in assets if a['operational_status'] == 'active'])
                }
            }
        }, 200
    
    def _get_network_topology(self):
        """Get power grid network topology"""
        
        # Mock network topology data
        network = {
            'nodes': [
                {'id': 'SUB001', 'name': 'Mumbai North', 'type': 'substation', 'voltage': '400kV', 
                 'coordinates': {'lat': 19.0760, 'lng': 72.8777}, 'capacity': 1200},
                {'id': 'SUB002', 'name': 'Delhi East', 'type': 'substation', 'voltage': '765kV',
                 'coordinates': {'lat': 28.6139, 'lng': 77.2090}, 'capacity': 2000},
                {'id': 'SUB003', 'name': 'Bangalore West', 'type': 'substation', 'voltage': '400kV',
                 'coordinates': {'lat': 12.9716, 'lng': 77.5946}, 'capacity': 1500},
                {'id': 'GEN001', 'name': 'Karnataka Solar', 'type': 'generator', 'voltage': '220kV',
                 'coordinates': {'lat': 15.3173, 'lng': 75.7139}, 'capacity': 500},
                {'id': 'LOAD001', 'name': 'Mumbai Industrial', 'type': 'load_center', 'voltage': '400kV',
                 'coordinates': {'lat': 19.0825, 'lng': 72.8428}, 'demand': 800}
            ],
            'edges': [
                {'id': 'LINE001', 'source': 'SUB001', 'target': 'SUB003', 'type': 'transmission_line',
                 'voltage': '400kV', 'capacity': 800, 'length_km': 840, 'status': 'active'},
                {'id': 'LINE002', 'source': 'SUB002', 'target': 'SUB001', 'type': 'transmission_line',
                 'voltage': '765kV', 'capacity': 1500, 'length_km': 1150, 'status': 'active'},
                {'id': 'LINE003', 'source': 'GEN001', 'target': 'SUB003', 'type': 'transmission_line',
                 'voltage': '220kV', 'capacity': 500, 'length_km': 280, 'status': 'active'},
                {'id': 'DIST001', 'source': 'SUB001', 'target': 'LOAD001', 'type': 'distribution',
                 'voltage': '400kV', 'capacity': 800, 'length_km': 12, 'status': 'active'}
            ]
        }
        
        # Calculate network statistics
        network_stats = {
            'total_nodes': len(network['nodes']),
            'total_edges': len(network['edges']),
            'substations': len([n for n in network['nodes'] if n['type'] == 'substation']),
            'generators': len([n for n in network['nodes'] if n['type'] == 'generator']),
            'load_centers': len([n for n in network['nodes'] if n['type'] == 'load_center']),
            'total_transmission_capacity': sum(e['capacity'] for e in network['edges'] if e['type'] == 'transmission_line'),
            'total_line_length': sum(e['length_km'] for e in network['edges']),
            'network_availability': 99.2  # Mock availability percentage
        }
        
        return {
            'success': True,
            'data': {
                'network': network,
                'statistics': network_stats,
                'topology_type': 'mesh_with_rings',
                'redundancy_level': 'high'
            }
        }, 200
    
    def _get_regional_data(self):
        """Get regional analysis data"""
        
        # Mock regional data
        regions = [
            {
                'region_id': 'WR',
                'name': 'Western Region',
                'states': ['Maharashtra', 'Gujarat', 'Goa', 'Madhya Pradesh', 'Chhattisgarh'],
                'center_coordinates': {'lat': 19.7515, 'lng': 75.7139},
                'total_projects': 45,
                'active_projects': 28,
                'total_investment': 125000,  # in crores
                'power_demand_mw': 45000,
                'generation_capacity_mw': 48000,
                'transmission_length_km': 12500,
                'avg_project_cost': 2778,
                'risk_profile': {
                    'high_risk_projects': 8,
                    'medium_risk_projects': 22,
                    'low_risk_projects': 15
                },
                'environmental_factors': {
                    'coastal_exposure': 30,  # percentage
                    'seismic_risk': 'medium',
                    'cyclone_prone_areas': 25,
                    'industrial_density': 'high'
                }
            },
            {
                'region_id': 'NR',
                'name': 'Northern Region',
                'states': ['Delhi', 'Punjab', 'Haryana', 'Rajasthan', 'Uttar Pradesh', 'Himachal Pradesh'],
                'center_coordinates': {'lat': 28.7041, 'lng': 77.1025},
                'total_projects': 38,
                'active_projects': 24,
                'total_investment': 98000,
                'power_demand_mw': 42000,
                'generation_capacity_mw': 38000,
                'transmission_length_km': 15200,
                'avg_project_cost': 2579,
                'risk_profile': {
                    'high_risk_projects': 6,
                    'medium_risk_projects': 18,
                    'low_risk_projects': 14
                },
                'environmental_factors': {
                    'coastal_exposure': 0,
                    'seismic_risk': 'high',
                    'extreme_weather': 40,
                    'dust_storms': 'frequent'
                }
            },
            {
                'region_id': 'SR',
                'name': 'Southern Region',
                'states': ['Karnataka', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Kerala'],
                'center_coordinates': {'lat': 13.0827, 'lng': 80.2707},
                'total_projects': 52,
                'active_projects': 31,
                'total_investment': 145000,
                'power_demand_mw': 38000,
                'generation_capacity_mw': 42000,
                'transmission_length_km': 11800,
                'avg_project_cost': 2788,
                'risk_profile': {
                    'high_risk_projects': 9,
                    'medium_risk_projects': 26,
                    'low_risk_projects': 17
                },
                'environmental_factors': {
                    'coastal_exposure': 45,
                    'seismic_risk': 'low',
                    'monsoon_impact': 'high',
                    'renewable_potential': 'excellent'
                }
            }
        ]
        
        # Calculate regional comparisons
        total_investment = sum(r['total_investment'] for r in regions)
        total_projects = sum(r['total_projects'] for r in regions)
        
        regional_comparison = {
            'investment_share': {r['name']: round(r['total_investment']/total_investment*100, 1) for r in regions},
            'project_share': {r['name']: round(r['total_projects']/total_projects*100, 1) for r in regions},
            'efficiency_metrics': {
                r['name']: {
                    'cost_per_mw': round(r['total_investment']*10/r['generation_capacity_mw'], 2),
                    'project_density': round(r['total_projects']/len(r['states']), 1),
                    'completion_rate': round(r['active_projects']/r['total_projects']*100, 1)
                } for r in regions
            }
        }
        
        return {
            'success': True,
            'data': {
                'regions': regions,
                'regional_comparison': regional_comparison,
                'national_summary': {
                    'total_regions': len(regions),
                    'total_investment': total_investment,
                    'total_projects': total_projects,
                    'avg_regional_investment': round(total_investment/len(regions), 0)
                }
            }
        }, 200
    
    def _get_comprehensive_geospatial_data(self):
        """Get comprehensive geospatial data combining all types"""
        
        projects = self._get_project_locations()[0]['data']
        assets = self._get_asset_locations()[0]['data']
        network = self._get_network_topology()[0]['data']
        regions = self._get_regional_data()[0]['data']
        
        return {
            'success': True,
            'data': {
                'projects': projects,
                'assets': assets,
                'network': network,
                'regions': regions,
                'map_settings': {
                    'default_center': {'lat': 20.5937, 'lng': 78.9629},  # India center
                    'default_zoom': 5,
                    'layer_visibility': {
                        'projects': True,
                        'assets': True,
                        'network': False,
                        'regions': True
                    }
                }
            }
        }, 200
    
    def _get_coordinates_for_location(self, location):
        """Get mock coordinates for a location string"""
        # Mock coordinate mapping - in production would use geocoding service
        location_coords = {
            'Maharashtra/Mumbai': {'lat': 19.0760, 'lng': 72.8777},
            'Maharashtra/Pune': {'lat': 18.5204, 'lng': 73.8567},
            'Delhi/East Delhi': {'lat': 28.6139, 'lng': 77.2090},
            'Delhi/South Delhi': {'lat': 28.5355, 'lng': 77.3910},
            'Karnataka/Bangalore': {'lat': 12.9716, 'lng': 77.5946},
            'Karnataka/Mysore': {'lat': 12.2958, 'lng': 76.6394},
            'Tamil Nadu/Chennai': {'lat': 13.0827, 'lng': 80.2707},
            'Tamil Nadu/Coimbatore': {'lat': 11.0168, 'lng': 76.9558},
            'Gujarat/Ahmedabad': {'lat': 23.0225, 'lng': 72.5714},
            'Gujarat/Surat': {'lat': 21.1702, 'lng': 72.8311},
            'Rajasthan/Jaipur': {'lat': 26.9124, 'lng': 75.7873},
            'Uttar Pradesh/Lucknow': {'lat': 26.8467, 'lng': 80.9462}
        }
        
        return location_coords.get(location, {'lat': 20.5937, 'lng': 78.9629})  # Default to India center
    
    def _calculate_completion_percentage(self, project):
        """Calculate mock completion percentage based on project status"""
        status_completion = {
            'Planning': 10,
            'In Progress': 45,
            'Testing': 80,
            'Completed': 100,
            'On Hold': 25,
            'Cancelled': 0
        }
        
        return status_completion.get(project.status, 0)
    
    def _calculate_map_bounds(self, locations):
        """Calculate map bounds for given locations"""
        if not locations:
            return None
        
        lats = [loc['coordinates']['lat'] for loc in locations if loc['coordinates']]
        lngs = [loc['coordinates']['lng'] for loc in locations if loc['coordinates']]
        
        if not lats or not lngs:
            return None
        
        return {
            'north': max(lats),
            'south': min(lats),
            'east': max(lngs),
            'west': min(lngs)
        }


class GeospatialSearchResource(Resource):
    """
    Resource for geospatial search and filtering
    """
    
    def post(self):
        """
        Search geospatial data based on criteria
        
        Expected JSON format:
        {
            "search_type": "projects|assets|network",
            "filters": {
                "region": "Western Region",
                "state": "Maharashtra",
                "project_type": "substation",
                "status": "active",
                "risk_level": "high",
                "radius_km": 50,
                "center_point": {"lat": 19.0760, "lng": 72.8777}
            }
        }
        """
        try:
            data = request.json or {}
            search_type = data.get('search_type', 'projects')
            filters = data.get('filters', {})
            
            if search_type == 'projects':
                results = self._search_projects(filters)
            elif search_type == 'assets':
                results = self._search_assets(filters)
            elif search_type == 'network':
                results = self._search_network(filters)
            else:
                return {
                    'success': False,
                    'message': f'Unknown search type: {search_type}'
                }, 400
            
            return {
                'success': True,
                'data': {
                    'search_type': search_type,
                    'filters_applied': filters,
                    'results': results,
                    'result_count': len(results) if isinstance(results, list) else 1
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error in geospatial search: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _search_projects(self, filters):
        """Search projects based on geospatial filters"""
        # Get all project locations
        projects_data = self._get_project_locations()[0]['data']['projects']
        
        # Apply filters
        filtered_projects = []
        for project in projects_data:
            # State filter
            if 'state' in filters:
                if '/' in project['location']:
                    project_state = project['location'].split('/')[0]
                    if project_state.lower() != filters['state'].lower():
                        continue
            
            # Project type filter
            if 'project_type' in filters:
                if project['project_type'].lower() != filters['project_type'].lower():
                    continue
            
            # Status filter
            if 'status' in filters:
                if project['status'].lower() != filters['status'].lower():
                    continue
            
            # Risk level filter
            if 'risk_level' in filters:
                if project.get('risk', '').lower() != filters['risk_level'].lower():
                    continue
            
            # Radius filter (if center point provided)
            if 'center_point' in filters and 'radius_km' in filters:
                distance = self._calculate_distance(
                    filters['center_point'],
                    project['coordinates']
                )
                if distance > filters['radius_km']:
                    continue
            
            filtered_projects.append(project)
        
        return filtered_projects
    
    def _search_assets(self, filters):
        """Search assets based on filters"""
        assets_data = self._get_asset_locations()[0]['data']['assets']
        
        filtered_assets = []
        for asset in assets_data:
            # Asset type filter
            if 'asset_type' in filters:
                if asset['type'].lower() != filters['asset_type'].lower():
                    continue
            
            # Voltage level filter
            if 'voltage_level' in filters:
                if asset['voltage_level'].lower() != filters['voltage_level'].lower():
                    continue
            
            # Status filter
            if 'status' in filters:
                if asset['operational_status'].lower() != filters['status'].lower():
                    continue
            
            filtered_assets.append(asset)
        
        return filtered_assets
    
    def _search_network(self, filters):
        """Search network elements based on filters"""
        network_data = self._get_network_topology()[0]['data']['network']
        
        result = {
            'nodes': [],
            'edges': []
        }
        
        # Filter nodes
        for node in network_data['nodes']:
            if 'node_type' in filters:
                if node['type'].lower() != filters['node_type'].lower():
                    continue
            
            if 'voltage' in filters:
                if node['voltage'].lower() != filters['voltage'].lower():
                    continue
            
            result['nodes'].append(node)
        
        # Filter edges
        for edge in network_data['edges']:
            if 'edge_type' in filters:
                if edge['type'].lower() != filters['edge_type'].lower():
                    continue
            
            if 'voltage' in filters:
                if edge['voltage'].lower() != filters['voltage'].lower():
                    continue
            
            result['edges'].append(edge)
        
        return result
    
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two points in kilometers (Haversine formula)"""
        import math
        
        # Convert latitude and longitude from decimal degrees to radians
        lat1, lon1 = math.radians(point1['lat']), math.radians(point1['lng'])
        lat2, lon2 = math.radians(point2['lat']), math.radians(point2['lng'])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r


class GeospatialExportResource(Resource):
    """
    Resource for exporting geospatial data in various formats
    """
    
    def post(self):
        """
        Export geospatial data
        
        Expected JSON format:
        {
            "export_type": "projects|assets|network|regions",
            "format": "geojson|kml|csv",
            "filters": {...}
        }
        """
        try:
            data = request.json or {}
            export_type = data.get('export_type', 'projects')
            format_type = data.get('format', 'geojson')
            filters = data.get('filters', {})
            
            if export_type == 'projects':
                geospatial_data = self._get_project_locations()[0]['data']['projects']
            elif export_type == 'assets':
                geospatial_data = self._get_asset_locations()[0]['data']['assets']
            else:
                return {
                    'success': False,
                    'message': f'Export not supported for type: {export_type}'
                }, 400
            
            if format_type == 'geojson':
                exported_data = self._convert_to_geojson(geospatial_data, export_type)
            elif format_type == 'csv':
                exported_data = self._convert_to_csv(geospatial_data, export_type)
            else:
                return {
                    'success': False,
                    'message': f'Unsupported format: {format_type}'
                }, 400
            
            return {
                'success': True,
                'data': {
                    'export_type': export_type,
                    'format': format_type,
                    'exported_data': exported_data,
                    'metadata': {
                        'total_features': len(geospatial_data),
                        'generated_at': datetime.utcnow().isoformat(),
                        'filters_applied': filters
                    }
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error exporting geospatial data: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }, 500
    
    def _convert_to_geojson(self, data, data_type):
        """Convert data to GeoJSON format"""
        
        features = []
        
        for item in data:
            if data_type == 'projects':
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [item['coordinates']['lng'], item['coordinates']['lat']]
                    },
                    "properties": {
                        "project_id": item['project_id'],
                        "name": item['name'],
                        "project_type": item['project_type'],
                        "status": item['status'],
                        "risk": item.get('risk'),
                        "cost": item['base_estimated_cost'],
                        "timeline": item['planned_timeline_months']
                    }
                }
            
            elif data_type == 'assets':
                if item['type'] == 'transmission_line':
                    # Handle transmission lines as LineString
                    coordinates = [[coord['lng'], coord['lat']] for coord in item['coordinates']]
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coordinates
                        },
                        "properties": {
                            "asset_id": item['asset_id'],
                            "name": item['name'],
                            "type": item['type'],
                            "voltage_level": item['voltage_level'],
                            "capacity": item['capacity_mw'],
                            "length_km": item.get('length_km')
                        }
                    }
                else:
                    # Handle substations and generators as Points
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [item['coordinates']['lng'], item['coordinates']['lat']]
                        },
                        "properties": {
                            "asset_id": item['asset_id'],
                            "name": item['name'],
                            "type": item['type'],
                            "voltage_level": item['voltage_level'],
                            "capacity": item['capacity_mw'],
                            "status": item['operational_status']
                        }
                    }
            
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson
    
    def _convert_to_csv(self, data, data_type):
        """Convert data to CSV format"""
        import io
        import csv
        
        output = io.StringIO()
        
        if data_type == 'projects':
            fieldnames = ['project_id', 'name', 'project_type', 'status', 'risk', 'cost', 'timeline', 'lat', 'lng', 'location']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                writer.writerow({
                    'project_id': item['project_id'],
                    'name': item['name'],
                    'project_type': item['project_type'],
                    'status': item['status'],
                    'risk': item.get('risk', ''),
                    'cost': item['base_estimated_cost'],
                    'timeline': item['planned_timeline_months'],
                    'lat': item['coordinates']['lat'],
                    'lng': item['coordinates']['lng'],
                    'location': item['location']
                })
        
        elif data_type == 'assets':
            fieldnames = ['asset_id', 'name', 'type', 'voltage_level', 'capacity', 'status', 'lat', 'lng']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                if item['type'] != 'transmission_line':
                    writer.writerow({
                        'asset_id': item['asset_id'],
                        'name': item['name'],
                        'type': item['type'],
                        'voltage_level': item['voltage_level'],
                        'capacity': item['capacity_mw'],
                        'status': item['operational_status'],
                        'lat': item['coordinates']['lat'],
                        'lng': item['coordinates']['lng']
                    })
        
        csv_data = output.getvalue()
        output.close()
        
        return csv_data