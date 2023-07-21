import React from 'react';

const Header: React.FC = () => {
    return (
        <header className="bg-blue-500 p-4">
            <nav className="flex justify-between items-center">
                <div className="text-white font-bold text-xl">My App</div>
                <ul className="flex space-x-4">
                    <li className="text-white">Home</li>
                    <li className="text-white">About</li>
                    <li className="text-white">Contact</li>
                </ul>
            </nav>
        </header>
    );
};

export default Header;
