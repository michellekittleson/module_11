import { Link } from 'react-router-dom';

function NotFound() {
    return (
        <div>
            <h4>404 - Not Found</h4>
            <p>Sorry, the page you are looking for does not exist.</p>
            <p>
                You can always go back to the <Link to="/">Homepage</Link>.
            </p>
        </div>
    )
}

export default NotFound;



