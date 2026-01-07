import type { Note } from '../../types';

interface NoteCardProps {
  note: Note;
}

export function NoteCard({ note }: NoteCardProps) {
  const formatDate = new Date(note.created_at).toLocaleString();

  return (
    <li className="note-card">
      <article>
        <h3>{note.title}</h3>
        <p>{note.content}</p>
        <time dateTime={note.created_at}>{formatDate}</time>
      </article>
    </li>
  );
}
