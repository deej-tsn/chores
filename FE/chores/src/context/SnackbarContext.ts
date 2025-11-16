import { createContext, createElement, useState } from "react";
import type { ReactNode } from "react";

type SnackbarContextType = {
    showSnackbar: number | undefined;
    setEditPanelState: (state: number | undefined) => void;
}

const editPanelContext = createContext<SnackbarContextType>({
    showSnackbar: undefined,
    setEditPanelState: () => {},
});

function EditPanelProvider({ children }: { children: ReactNode }) {
    const [showEditPanel, setEditPanelState] = useState<number | undefined>(undefined);

    return createElement(
        editPanelContext.Provider,
        { value: { showSnackbar: showEditPanel, setEditPanelState } },
        children
    );
}

export { editPanelContext, EditPanelProvider };