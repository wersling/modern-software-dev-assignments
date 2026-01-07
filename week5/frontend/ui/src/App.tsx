import { NotesList } from './components/notes/NotesList';
import { ActionItemsList } from './components/action-items/ActionItemsList';
import './App.css';

function App() {
  return (
    <main className="app-main">
      <h1>Modern Software Dev Starter</h1>
      <NotesList />
      <ActionItemsList />
    </main>
  );
}

export default App;
