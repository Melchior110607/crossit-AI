'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Package, 
  Search, 
  Plus,
  Filter,
  Eye,
  Edit,
  Trash2,
  Copy,
  ShoppingCart,
  TrendingUp,
  Star,
  LayoutGrid,
  LayoutList,
  MoreVertical
} from 'lucide-react';
import Link from 'next/link';

export default function ProductsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'draft'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState<typeof products[0] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock data - à remplacer par des vraies données de l'API
  const products = [
    {
      id: '1',
      name: 'Premium Wireless Headphones',
      sku: 'WH-1000XM5',
      price: 349.99,
      stock: 45,
      status: 'active',
      marketplaces: 3,
      sales: 127,
      rating: 4.8,
      category: 'Electronics',
    },
    {
      id: '2',
      name: 'Ergonomic Wireless Mouse',
      sku: 'MX-MASTER-3',
      price: 99.99,
      stock: 78,
      status: 'active',
      marketplaces: 5,
      sales: 243,
      rating: 4.9,
      category: 'Electronics',
    },
    {
      id: '3',
      name: 'Mechanical Keyboard RGB',
      sku: 'KB-RGB-PRO',
      price: 179.99,
      stock: 23,
      status: 'active',
      marketplaces: 2,
      sales: 89,
      rating: 4.7,
      category: 'Electronics',
    },
    {
      id: '4',
      name: 'USB-C Hub 7-in-1',
      sku: 'HUB-7IN1',
      price: 59.99,
      stock: 156,
      status: 'active',
      marketplaces: 4,
      sales: 312,
      rating: 4.6,
      category: 'Accessories',
    },
    {
      id: '5',
      name: 'Laptop Stand Adjustable',
      sku: 'LS-ADJ-PRO',
      price: 49.99,
      stock: 0,
      status: 'draft',
      marketplaces: 0,
      sales: 0,
      rating: 0,
      category: 'Accessories',
    },
    {
      id: '6',
      name: 'Webcam HD 1080p',
      sku: 'WC-HD-1080',
      price: 79.99,
      stock: 64,
      status: 'active',
      marketplaces: 3,
      sales: 156,
      rating: 4.5,
      category: 'Electronics',
    },
  ];

  const filteredProducts = products.filter(product => {
    const matchesSearch = 
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || product.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: products.length,
    active: products.filter(p => p.status === 'active').length,
    draft: products.filter(p => p.status === 'draft').length,
    totalValue: products.reduce((sum, p) => sum + (p.price * p.stock), 0),
  };

  // Skeleton Loader Component - Plus compact
  const ProductSkeleton = () => (
    <Card className="glass-effect border-warmgold/20 overflow-hidden">
      <Skeleton className="h-32 w-full" />
      <CardContent className="p-4">
        <Skeleton className="h-5 w-3/4 mb-2" />
        <Skeleton className="h-3 w-1/2 mb-3" />
        <Skeleton className="h-6 w-full mb-3" />
        <div className="grid grid-cols-3 gap-2">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
        </div>
      </CardContent>
    </Card>
  );

  return (
    <TooltipProvider>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-darktext mb-2 flex items-center gap-3">
              <ShoppingCart className="w-8 h-8 text-warmgold" />
              Product Marketplace
            </h1>
            <p className="text-darktext/60">
              Browse and manage your premium product catalog
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Toggle Grid/Table View */}
            <div className="flex items-center gap-1 p-1 bg-lightgray rounded-lg border border-warmgold/20">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setViewMode('grid')}
                className={viewMode === 'grid' ? 'bg-warmgold/20 text-warmgold' : 'text-darktext/60'}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setViewMode('table')}
                className={viewMode === 'table' ? 'bg-warmgold/20 text-warmgold' : 'text-darktext/60'}
              >
                <LayoutList className="h-4 w-4" />
              </Button>
            </div>
            
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  asChild
                  className="bg-gradient-gold hover:opacity-90 text-white font-semibold shadow-premium"
                >
                  <Link href="/dashboard/products/new">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Product
                  </Link>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Create a new product</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </div>


      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-darktext/40 w-5 h-5" />
          <Input
            placeholder="Search products by name or SKU..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-lightgray border-warmgold/20 text-darktext placeholder:text-darktext/40 focus:border-warmgold focus:ring-gold"
          />
        </div>

        {/* Status Filter */}
        <div className="flex gap-2">
          <Button
            variant={filterStatus === 'all' ? 'default' : 'outline'}
            onClick={() => setFilterStatus('all')}
            size="sm"
            className={filterStatus === 'all' 
              ? 'bg-gradient-gold text-carbon' 
              : 'bg-lightgray/50 border-warmgold/20 text-darktext hover:bg-lightgray'
            }
          >
            All
          </Button>
          <Button
            variant={filterStatus === 'active' ? 'default' : 'outline'}
            onClick={() => setFilterStatus('active')}
            size="sm"
            className={filterStatus === 'active' 
              ? 'bg-gradient-gold text-carbon' 
              : 'bg-lightgray/50 border-warmgold/20 text-darktext hover:bg-lightgray'
            }
          >
            Active
          </Button>
          <Button
            variant={filterStatus === 'draft' ? 'default' : 'outline'}
            onClick={() => setFilterStatus('draft')}
            size="sm"
            className={filterStatus === 'draft' 
              ? 'bg-gradient-gold text-carbon' 
              : 'bg-lightgray/50 border-warmgold/20 text-darktext hover:bg-lightgray'
            }
          >
            Draft
          </Button>
        </div>
      </div>

      {/* Skeleton Loading State */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {[...Array(8)].map((_, i) => (
            <ProductSkeleton key={i} />
          ))}
        </div>
      ) : viewMode === 'table' ? (
        /* Table View */
        <Card className="glass-effect border-warmgold/20 shadow-premium">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Stock</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Marketplaces</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredProducts.map((product) => (
                <TableRow key={product.id} className="hover:bg-lightgray/30">
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-warmgray to-lightcream flex items-center justify-center">
                        <Package className="w-5 h-5 text-warmgold" />
                      </div>
                      <div>
                        <p className="font-medium text-darktext">{product.name}</p>
                        <p className="text-xs text-darktext/60">{product.category}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-darktext/70">{product.sku}</TableCell>
                  <TableCell className="font-semibold text-warmgold">${product.price}</TableCell>
                  <TableCell>
                    <span className={`text-sm ${
                      product.stock === 0 ? 'text-destructive' :
                      product.stock < 30 ? 'text-skyblue' :
                      'text-darktext/70'
                    }`}>
                      {product.stock === 0 ? 'Out of stock' : `${product.stock} units`}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={product.status === 'active' ? 'gold' : 'electric'}>
                      {product.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{product.marketplaces} platforms</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="glass-effect border-warmgold/20">
                        <DropdownMenuItem className="cursor-pointer">
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer">
                          <Edit className="mr-2 h-4 w-4" />
                          Edit Product
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer">
                          <Copy className="mr-2 h-4 w-4" />
                          Duplicate
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          className="cursor-pointer text-destructive"
                          onClick={() => {
                            setProductToDelete(product);
                            setDeleteDialogOpen(true);
                          }}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      ) : (
        /* Products Grid - Style Marché - Plus compact */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredProducts.map((product) => (
          <Card
            key={product.id}
            className="glass-effect border-warmgold/20 shadow-premium hover:shadow-electric transition-all duration-300 hover:scale-105 group overflow-hidden"
          >
            {/* Product Image - Plus compact */}
            <div className="relative h-32 bg-gradient-to-br from-warmgray to-carbon border-b border-warmgold/20">
              <div className="absolute inset-0 flex items-center justify-center">
                <Package className="w-14 h-14 text-warmgold/30 group-hover:text-warmgold/50 transition-colors" />
              </div>
              
              {/* Status Badge */}
              <div className="absolute top-3 right-3">
                <Badge variant={product.status === 'active' ? 'gold' : 'electric'}>
                  {product.status}
                </Badge>
              </div>

              {/* Rating */}
              {product.rating > 0 && (
                <div className="absolute top-3 left-3 flex items-center gap-1 px-2 py-1 rounded-lg bg-carbon/80 backdrop-blur">
                  <Star className="w-3 h-3 text-warmgold fill-gold" />
                  <span className="text-xs font-semibold text-darktext">{product.rating}</span>
                </div>
              )}
            </div>

            <CardContent className="p-4">
              {/* Product Info - Plus compact */}
              <div className="mb-3">
                <h3 className="text-base font-bold text-darktext group-hover:text-warmgold transition-colors mb-1 line-clamp-1">
                  {product.name}
                </h3>
                <p className="text-xs text-darktext/50 mb-1">SKU: {product.sku}</p>
                <Badge variant="outline" className="text-xs">
                  {product.category}
                </Badge>
              </div>

              {/* Price & Stock - Plus compact */}
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-xl font-bold text-warmgold">${product.price}</p>
                  <p className={`text-xs ${
                    product.stock === 0 ? 'text-destructive' :
                    product.stock < 30 ? 'text-skyblue' :
                    'text-darktext/60'
                  }`}>
                    {product.stock === 0 ? 'Out of stock' : `${product.stock} in stock`}
                  </p>
                </div>
                {product.sales > 0 && (
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-skyblue">
                      <TrendingUp className="w-4 h-4" />
                      <span className="text-xs font-semibold">{product.sales}</span>
                    </div>
                    <p className="text-xs text-darktext/50">sales</p>
                  </div>
                )}
              </div>

              {/* Marketplaces */}
              <div className="flex items-center justify-between mb-3 pb-3 border-b border-warmgold/10">
                <span className="text-xs text-darktext/60">Listed on</span>
                <Badge variant="gold">{product.marketplaces} marketplaces</Badge>
              </div>

              {/* Actions - Dropdown Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full bg-lightgray/30 border-warmgold/20 text-darktext hover:bg-lightgray hover:border-warmgold/40"
                  >
                    <MoreVertical className="h-4 w-4 mr-2" />
                    Actions
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="glass-effect border-warmgold/20 w-48">
                  <DropdownMenuItem className="cursor-pointer">
                    <Eye className="mr-2 h-4 w-4" />
                    View Details
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer">
                    <Edit className="mr-2 h-4 w-4" />
                    Edit Product
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer">
                    <Copy className="mr-2 h-4 w-4" />
                    Duplicate
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    className="cursor-pointer text-destructive"
                    onClick={() => {
                      setProductToDelete(product);
                      setDeleteDialogOpen(true);
                    }}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </CardContent>
          </Card>
          ))}
        </div>
      )}

      {filteredProducts.length === 0 && !isLoading && (
        <Card className="glass-effect border-warmgold/20">
          <CardContent className="text-center py-12">
            <Package className="w-16 h-16 text-darktext/40 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-darktext mb-2">No products found</h3>
            <p className="text-darktext/60 mb-6">
              {searchQuery
                ? "Try adjusting your search query"
                : "Get started by adding your first product"}
            </p>
            <Button
              asChild
              className="bg-gradient-gold hover:opacity-90 text-carbon font-semibold"
            >
              <Link href="/dashboard/products/new">
                <Plus className="mr-2 h-4 w-4" />
                Add Product
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="glass-effect border-warmgold/20">
          <DialogHeader>
            <DialogTitle className="text-darktext">Confirm Deletion</DialogTitle>
            <DialogDescription className="text-darktext/60">
              Are you sure you want to delete <span className="font-semibold text-darktext">{productToDelete?.name}</span>? 
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setDeleteDialogOpen(false)}
              className="border-warmgold/20"
            >
              Cancel
            </Button>
            <Button 
              variant="destructive"
              onClick={() => {
                // TODO: Call delete API
                console.log('Deleting product:', productToDelete?.id);
                setDeleteDialogOpen(false);
                setProductToDelete(null);
              }}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete Product
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </TooltipProvider>
  );
}
