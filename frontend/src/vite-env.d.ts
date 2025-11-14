interface ViteTypeOptions {
    strictImportMetaEnv: unknown
}

interface ImportMetaEnv {
    readonly VITE_COMPANY_NAME: string
    readonly VITE_APPLICATION_NAME: string
    readonly VITE_BACKEND_URL: string

    readonly VITE_DEV_JWT: string
    readonly VITE_DEV_JWT_NON_LOCAL: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}