---@type vim.lsp.Config
return {
  cmd = {
    'OmniSharp',
    '--zero-based-indices',
    '--hostPID',
    tostring(vim.fn.getpid()),
    'DotNet:enablePackageRestore=false',
    '--encoding',
    'utf-8',
    '--languageserver',
  },
  filetypes = { 'cs' },
  root_markers = { '.root', '.git' },
  capabilities = {
    workspace = {
      workspaceFolders = false,
    },
  },
  settings = {
    FormattingOptions = {
      EnableEditorConfigSupport = true,
      OrganizeImports = nil,
    },
    MsBuild = {
      LoadProjectsOnDemand = nil,
    },
    RoslynExtensionsOptions = {
      EnableAnalyzersSupport = nil,
      EnableImportCompletion = nil,
      AnalyzeOpenDocumentsOnly = nil,
      EnableDecompilationSupport = nil,
    },
    RenameOptions = {
      RenameInComments = nil,
      RenameOverloads = nil,
      RenameInStrings = nil,
    },
    Sdk = {
      IncludePrereleases = true,
    },
  },
}
