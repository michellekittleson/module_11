import { Routes, Route, Navigate } from 'react-router-dom';
import CustomerList from './components/CustomerList';
import NavigationBar from './components/NavigationBar';
import CustomerFormWrapper from './components/CustomerFormWrapper';
import NotFound from './components/NotFound';
import HomePage from './components/HomePage';
import ProductList from './components/ProductList';
import ProductForm from './components/ProductForm';
import './AppStyles.css';
import 'bootstrap/dist/css/bootstrap.min.css'


function App() {
  return (
    <div className="app-container">
      <NavigationBar />
      <Routes>
        <Route path='/' element={<HomePage />} />
        <Route path='./add-customer' element={<CustomerFormWrapper />} />
        <Route path='./edit-customer/:id' element={<CustomerFormWrapper />} />
        <Route path='/customers' element={<CustomerList />} />
        <Route path='/add-product' element={<ProductForm />} />
        <Route path='/edit-product/:id' element={<ProductForm />} />
        <Route path='/products' element={<ProductList />} />
        <Route path='*' element={<NotFound />} />
      </Routes>
    </div>
  );
}

export default App;
