// app/document/[file_id]/page.tsx
import { DocumentClientPage } from "./client-page"

interface PageProps {
  params: Promise<{ file_id: string }>
}

export default async function Page({ params }: PageProps) {
  const { file_id } = await params   // ✅ FIX: unwrap params
        
  return <DocumentClientPage fileId={file_id} />
}
