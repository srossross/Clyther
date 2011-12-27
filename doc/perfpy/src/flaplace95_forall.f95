! File flaplace95_forall.f90
! Author: Ramon Crehuet
subroutine timestep(u,n,m,dx,dy,error)
implicit none
real (kind=8), dimension(0:n-1,0:m-1), intent(inout):: u

real (kind=8), intent(in) :: dx,dy
real (kind=8), intent(out) :: error
integer, intent(in) :: n,m
real (kind=8), dimension(0:n-1,0:m-1) :: diff
real (kind=8) :: dx2,dy2,dnr_inv
integer :: i,j

!f2py intent(in) :: dx,dy
!f2py intent(in,out) :: u
!f2py intent(out) :: error
!f2py intent(hide) :: n,m

dx2 = dx*dx
dy2 = dy*dy
dnr_inv = 0.5d0 / (dx2+dy2)

diff=u

forall (i=1:n-2,j=1:m-2)
    u(i,j) = ((u(i-1,j) + u(i+1,j))*dy2+(u(i,j-1) + u(i,j+1))*dx2)*dnr_inv
end forall

error=sqrt(sum((u-diff)**2))

end subroutine
