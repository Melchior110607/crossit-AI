// React hook for products management
'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  getProducts, 
  getProduct,
  createProduct, 
  updateProduct, 
  deleteProduct,
  getProductsStats,
  type Product,
  type ProductStats,
  type CreateProductData,
  type UpdateProductData
} from '@/lib/api/products';

export function useProducts(params?: { status?: string; search?: string }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getProducts(params);
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch products');
      console.error('Error fetching products:', err);
    } finally {
      setIsLoading(false);
    }
  }, [params?.status, params?.search]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  return { products, isLoading, error, refetch: fetchProducts };
}

export function useProduct(id: string) {
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProduct() {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getProduct(id);
        setProduct(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch product');
        console.error('Error fetching product:', err);
      } finally {
        setIsLoading(false);
      }
    }

    if (id) {
      fetchProduct();
    }
  }, [id]);

  return { product, isLoading, error };
}

export function useProductsStats() {
  const [stats, setStats] = useState<ProductStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getProductsStats();
        setStats(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch stats');
        console.error('Error fetching stats:', err);
      } finally {
        setIsLoading(false);
      }
    }

    fetchStats();
  }, []);

  return { stats, isLoading, error };
}

export function useProductMutations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = async (data: CreateProductData): Promise<Product | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const product = await createProduct(data);
      return product;
    } catch (err: any) {
      setError(err.message || 'Failed to create product');
      console.error('Error creating product:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const update = async (id: string, data: UpdateProductData): Promise<Product | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const product = await updateProduct(id, data);
      return product;
    } catch (err: any) {
      setError(err.message || 'Failed to update product');
      console.error('Error updating product:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const remove = async (id: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await deleteProduct(id);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete product');
      console.error('Error deleting product:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return { create, update, remove, isLoading, error };
}

