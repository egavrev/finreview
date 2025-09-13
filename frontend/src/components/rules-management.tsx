"use client";

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ChevronDown, ChevronRight, Plus, Edit, Trash2, TestTube, BarChart3 } from 'lucide-react';
import { API_ENDPOINTS } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface RuleCategory {
  id: number;
  name: string;
  description?: string;
  color?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface MatchingRule {
  id: number;
  rule_type: 'exact' | 'keyword' | 'pattern';
  category: string;
  pattern: string;
  weight: number;
  priority: number;
  is_active: boolean;
  comments?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
  success_count: number;
  last_used?: string;
}

interface RuleTestResult {
  test_string: string;
  matches: boolean;
  confidence: number;
  rule_pattern: string;
  rule_type: string;
}

const RulesManagement: React.FC = () => {
  const [categories, setCategories] = useState<RuleCategory[]>([]);
  const [rules, setRules] = useState<MatchingRule[]>([]);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [showCreateRule, setShowCreateRule] = useState(false);
  const [showCreateCategory, setShowCreateCategory] = useState(false);
  const [editingRule, setEditingRule] = useState<MatchingRule | null>(null);
  const [editingCategory, setEditingCategory] = useState<RuleCategory | null>(null);
  const [testResults, setTestResults] = useState<RuleTestResult[]>([]);
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [testingRule, setTestingRule] = useState<MatchingRule | null>(null);

  // Form states
  const [newRule, setNewRule] = useState({
    rule_type: 'keyword' as const,
    category: '',
    pattern: '',
    weight: 85,
    priority: 0,
    comments: '',
  });

  const [newCategory, setNewCategory] = useState({
    name: '',
    description: '',
    color: '#FF6B6B',
  });

  useEffect(() => {
    if (token) {
      fetchCategories();
      fetchRules();
    }
  }, [token]);

  const fetchCategories = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.RULES.CATEGORIES, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        // Handle paginated response - extract items array
        setCategories(data.items || data);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchRules = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.RULES.RULES, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        // Handle paginated response - extract items array
        setRules(data.items || data);
      }
    } catch (error) {
      console.error('Error fetching rules:', error);
    }
  };

  const createRule = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.RULES.RULES, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newRule),
      });

      if (response.ok) {
        await fetchRules();
        setShowCreateRule(false);
        setNewRule({ rule_type: 'keyword', category: '', pattern: '', weight: 85, priority: 0, comments: '' });
      }
    } catch (error) {
      console.error('Error creating rule:', error);
    } finally {
      setLoading(false);
    }
  };

  const createCategory = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.RULES.CATEGORIES, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newCategory),
      });

      if (response.ok) {
        await fetchCategories();
        setShowCreateCategory(false);
        setNewCategory({ name: '', description: '', color: '#FF6B6B' });
      }
    } catch (error) {
      console.error('Error creating category:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateCategory = async () => {
    if (!editingCategory) return;

    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.RULES.CATEGORY_BY_ID(editingCategory.id), {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newCategory),
      });

      if (response.ok) {
        await fetchCategories();
        setEditingCategory(null);
        setNewCategory({ name: '', description: '', color: '#FF6B6B' });
      }
    } catch (error) {
      console.error('Error updating category:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateRule = async () => {
    if (!editingRule) return;

    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.RULES.RULE_BY_ID(editingRule.id), {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newRule),
      });

      if (response.ok) {
        await fetchRules();
        setEditingRule(null);
        setNewRule({ rule_type: 'keyword', category: '', pattern: '', weight: 85, priority: 0, comments: '' });
      }
    } catch (error) {
      console.error('Error updating rule:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteRule = async (ruleId: number) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;

    try {
      const response = await fetch(API_ENDPOINTS.RULES.RULE_BY_ID(ruleId), {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchRules();
      }
    } catch (error) {
      console.error('Error deleting rule:', error);
    }
  };

  const testRule = async (rule: MatchingRule, testStrings: string[]) => {
    try {
      const response = await fetch(API_ENDPOINTS.RULES.RULE_TEST(rule.id), {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ rule_id: rule.id, test_strings: testStrings }),
      });

      if (response.ok) {
        const results = await response.json();
        setTestResults(results);
        setTestingRule(rule);
        setShowTestDialog(true);
      }
    } catch (error) {
      console.error('Error testing rule:', error);
    }
  };

  const filteredRules = (rules || []).filter(rule => {
    const categoryMatch = selectedCategory === 'all' || rule.category === selectedCategory;
    const typeMatch = selectedType === 'all' || rule.rule_type === selectedType;
    return categoryMatch && typeMatch;
  });

  const getRuleTypeColor = (type: string) => {
    switch (type) {
      case 'exact': return 'bg-green-100 text-green-800';
      case 'keyword': return 'bg-blue-100 text-blue-800';
      case 'pattern': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with action buttons */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Rules Management</h2>
          <p className="text-gray-600 mt-1">
            Manage operation matching rules and categories for automatic classification
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowCreateCategory(true)} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Add Category
          </Button>
          <Button onClick={() => setShowCreateRule(true)} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Add Rule
          </Button>
        </div>
      </div>
          {/* Categories section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Categories
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Loading categories...</p>
                </div>
              ) : (categories || []).length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {(categories || []).map((category) => (
                    <div
                      key={category.id}
                      className="p-4 border rounded-lg flex items-center justify-between"
                      style={{ borderLeftColor: category.color, borderLeftWidth: '4px' }}
                    >
                      <div>
                        <h4 className="font-medium">{category.name}</h4>
                        {category.description && (
                          <p className="text-sm text-gray-600">{category.description}</p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingCategory(category);
                            setNewCategory({
                              name: category.name,
                              description: category.description || '',
                              color: category.color || '#FF6B6B',
                            });
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No categories found</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Rules section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Matching Rules</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    Showing {filteredRules.length} of {(rules || []).length} rules
                  </p>
                </div>
                <div className="flex gap-4 items-end">
                  <div>
                    <Label className="text-sm font-medium">Category</Label>
                    <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Filter by category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Categories</SelectItem>
                        {(categories || []).length > 0 && (categories || []).map((category) => (
                          <SelectItem key={category.id} value={category.name}>
                            {category.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Type</Label>
                    <Select value={selectedType} onValueChange={setSelectedType}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Filter by type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="exact">Exact Match</SelectItem>
                        <SelectItem value="keyword">Keyword</SelectItem>
                        <SelectItem value="pattern">Pattern (Regex)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Loading rules...</p>
                </div>
              ) : filteredRules && filteredRules.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Type</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Pattern</TableHead>
                      <TableHead>Comments</TableHead>
                      <TableHead>Weight</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Usage</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRules.map((rule) => (
                      <TableRow key={rule.id}>
                        <TableCell>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRuleTypeColor(rule.rule_type)}`}>
                            {rule.rule_type}
                          </span>
                        </TableCell>
                        <TableCell>{rule.category}</TableCell>
                        <TableCell className="font-mono text-sm">{rule.pattern}</TableCell>
                        <TableCell className="max-w-xs truncate" title={rule.comments || ''}>
                          {rule.comments || '-'}
                        </TableCell>
                        <TableCell>{rule.weight}</TableCell>
                        <TableCell>{rule.priority}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div>{rule.usage_count} uses</div>
                            <div className="text-gray-500">
                              {rule.usage_count > 0 
                                ? `${((rule.success_count / rule.usage_count) * 100).toFixed(1)}% success`
                                : 'No usage'
                              }
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => testRule(rule, ['Test string 1', 'Test string 2'])}
                            >
                              <TestTube className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditingRule(rule);
                                setNewRule({
                                  rule_type: rule.rule_type,
                                  category: rule.category,
                                  pattern: rule.pattern,
                                  weight: rule.weight,
                                  priority: rule.priority,
                                  comments: rule.comments || '',
                                });
                              }}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteRule(rule.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No rules found</p>
                </div>
              )}
                      </CardContent>
        </Card>

            {/* Create/Edit Rule Dialog */}
      <Dialog open={showCreateRule || editingRule !== null} onOpenChange={(open) => {
        if (!open) {
          setShowCreateRule(false);
          setEditingRule(null);
          setNewRule({ rule_type: 'keyword', category: '', pattern: '', weight: 85, priority: 0, comments: '' });
        }
      }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingRule ? 'Edit Rule' : 'Create New Rule'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="rule-type">Rule Type</Label>
              <Select value={newRule.rule_type} onValueChange={(value: any) => setNewRule({ ...newRule, rule_type: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="exact">Exact Match</SelectItem>
                  <SelectItem value="keyword">Keyword</SelectItem>
                  <SelectItem value="pattern">Pattern (Regex)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="category">Category</Label>
              <Select value={newRule.category} onValueChange={(value) => setNewRule({ ...newRule, category: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {(categories || []).length > 0 ? (categories || []).map((category) => (
                    <SelectItem key={category.id} value={category.name}>
                      {category.name}
                    </SelectItem>
                  )) : (
                    <SelectItem value="loading" disabled>Loading categories...</SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="pattern">Pattern</Label>
              <Input
                id="pattern"
                value={newRule.pattern}
                onChange={(e) => setNewRule({ ...newRule, pattern: e.target.value })}
                placeholder={newRule.rule_type === 'pattern' ? 'Enter regex pattern' : 'Enter pattern'}
              />
            </div>
            <div>
              <Label htmlFor="comments">Comments (Optional)</Label>
              <Input
                id="comments"
                value={newRule.comments}
                onChange={(e) => setNewRule({ ...newRule, comments: e.target.value })}
                placeholder="Enter comments or notes for this rule"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="weight">Weight (0-100)</Label>
                <Input
                  id="weight"
                  type="number"
                  min="0"
                  max="100"
                  value={newRule.weight}
                  onChange={(e) => setNewRule({ ...newRule, weight: parseInt(e.target.value) })}
                />
              </div>
              <div>
                <Label htmlFor="priority">Priority</Label>
                <Input
                  id="priority"
                  type="number"
                  value={newRule.priority}
                  onChange={(e) => setNewRule({ ...newRule, priority: parseInt(e.target.value) })}
                />
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => {
                setShowCreateRule(false);
                setEditingRule(null);
                setNewRule({ rule_type: 'keyword', category: '', pattern: '', weight: 85, priority: 0, comments: '' });
              }}>
                Cancel
              </Button>
              <Button onClick={editingRule ? updateRule : createRule} disabled={loading}>
                {loading ? (editingRule ? 'Updating...' : 'Creating...') : (editingRule ? 'Update Rule' : 'Create Rule')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Category Dialog */}
      <Dialog open={showCreateCategory || editingCategory !== null} onOpenChange={(open) => {
        if (!open) {
          setShowCreateCategory(false);
          setEditingCategory(null);
          setNewCategory({ name: '', description: '', color: '#FF6B6B' });
        }
      }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingCategory ? 'Edit Category' : 'Create New Category'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="category-name">Name</Label>
              <Input
                id="category-name"
                value={newCategory.name}
                onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                placeholder="Enter category name"
              />
            </div>
            <div>
              <Label htmlFor="category-description">Description</Label>
              <Input
                id="category-description"
                value={newCategory.description}
                onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                placeholder="Enter description"
              />
            </div>
            <div>
              <Label htmlFor="category-color">Color</Label>
              <Input
                id="category-color"
                type="color"
                value={newCategory.color}
                onChange={(e) => setNewCategory({ ...newCategory, color: e.target.value })}
              />
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => {
                setShowCreateCategory(false);
                setEditingCategory(null);
                setNewCategory({ name: '', description: '', color: '#FF6B6B' });
              }}>
                Cancel
              </Button>
              <Button onClick={editingCategory ? updateCategory : createCategory} disabled={loading}>
                {loading ? (editingCategory ? 'Updating...' : 'Creating...') : (editingCategory ? 'Update Category' : 'Create Category')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Test Results Dialog */}
      <Dialog open={showTestDialog} onOpenChange={setShowTestDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Test Results for Rule: {testingRule?.pattern}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Test String</TableHead>
                  <TableHead>Matches</TableHead>
                  <TableHead>Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {testResults.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-mono">{result.test_string}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        result.matches ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {result.matches ? 'Yes' : 'No'}
                      </span>
                    </TableCell>
                    <TableCell>{result.confidence}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RulesManagement;
